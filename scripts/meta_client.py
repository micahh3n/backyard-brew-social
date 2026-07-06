"""
meta_client.py - Facebook + Instagram publishing via the Meta Graph API.

This is the ONLY module that talks to the live accounts. It handles:
  - Facebook Page photo post (with location tag = the bar's own Page)
  - Instagram feed post (image_url + clean caption + best-effort location)
  - Instagram first-comment hashtags (caption stays clean)
  - Instagram Story auto-repost of the same image
  - building the public raw.githubusercontent.com URL Instagram requires
  - a long-lived token expiry check for the 60-day reminder

Credentials come from environment variables (GitHub Secrets in production):
  META_PAGE_ACCESS_TOKEN, META_PAGE_ID, META_IG_USER_ID
"""

from __future__ import annotations

import os
import time
import urllib.parse

import requests

import config

GRAPH = "https://graph.facebook.com/v21.0"


class MetaError(Exception):
    """Raised when a Graph API call fails in a way that should stop that post."""


def _token() -> str:
    tok = os.environ.get("META_PAGE_ACCESS_TOKEN")
    if not tok:
        raise MetaError("META_PAGE_ACCESS_TOKEN is not set")
    return tok


def _page_id() -> str:
    pid = os.environ.get("META_PAGE_ID")
    if not pid:
        raise MetaError("META_PAGE_ID is not set")
    return pid


def _ig_id() -> str:
    iid = os.environ.get("META_IG_USER_ID")
    if not iid:
        raise MetaError("META_IG_USER_ID is not set")
    return iid


def _post(path, data):
    r = requests.post(f"{GRAPH}/{path}", data={**data, "access_token": _token()}, timeout=60)
    body = r.json() if r.content else {}
    if r.status_code >= 400 or "error" in body:
        raise MetaError(f"POST {path} failed: {body.get('error', body)}")
    return body


def _get(path, params):
    r = requests.get(f"{GRAPH}/{path}", params={**params, "access_token": _token()}, timeout=60)
    body = r.json() if r.content else {}
    if r.status_code >= 400 or "error" in body:
        raise MetaError(f"GET {path} failed: {body.get('error', body)}")
    return body


# ---------------------------------------------------------------------------
# Public image URL (Instagram cannot accept a file upload -- it needs a URL)
# ---------------------------------------------------------------------------
def public_image_url(repo_relative_path: str) -> str:
    """Build the raw.githubusercontent.com URL for a file in this repo.

    Owner/repo/branch are read from the environment GitHub Actions provides, so
    nothing is hardcoded. repo_relative_path uses forward slashes from repo root.
    """
    repo = os.environ.get("GITHUB_REPOSITORY")  # "owner/repo"
    branch = os.environ.get("GITHUB_REF_NAME") or os.environ.get("GITHUB_BRANCH") or "main"
    if not repo:
        # Local dry-run fallback: let the owner set it explicitly.
        repo = os.environ.get("REPO_SLUG", "OWNER/REPO")
    path = urllib.parse.quote(repo_relative_path.replace("\\", "/"))
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"


# ---------------------------------------------------------------------------
# Location handling
# ---------------------------------------------------------------------------
_ig_location_cache = None


def _find_ig_location_id():
    """Best-effort lookup of an Instagram location_id for the bar.

    Uses the place search near the bar's coordinates. Returns None on any
    failure -- a missing location tag must never block a post.
    """
    global _ig_location_cache
    if _ig_location_cache is not None:
        return _ig_location_cache or None
    try:
        b = config.BUSINESS
        res = _get("search", {
            "type": "place",
            "q": b["name"],
            "center": f"{b['latitude']},{b['longitude']}",
            "distance": 2000,
            "fields": "id,name",
        })
        for place in res.get("data", []):
            if b["name"].lower() in place.get("name", "").lower():
                _ig_location_cache = place["id"]
                return _ig_location_cache
        if res.get("data"):
            _ig_location_cache = res["data"][0]["id"]
            return _ig_location_cache
    except Exception as exc:
        print(f"[meta_client] IG location lookup failed (posting without tag): {exc}")
    _ig_location_cache = ""
    return None


# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------
def post_facebook(image_url: str, caption: str) -> str:
    """Publish a photo post to the Facebook Page, tagged at the bar's location.

    The location tag on a Page's own post is the Page itself (place=PAGE_ID).
    If tagging errors, retry once without it so the post still goes out.
    """
    pid = _page_id()
    data = {"url": image_url, "message": caption, "place": pid}
    try:
        res = _post(f"{pid}/photos", data)
    except MetaError as exc:
        print(f"[meta_client] FB post with place failed, retrying untagged: {exc}")
        res = _post(f"{pid}/photos", {"url": image_url, "message": caption})
    return res.get("post_id") or res.get("id", "")


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------
def _wait_container_ready(creation_id, tries=10, delay=3):
    """Poll until the IG media container finishes processing."""
    for _ in range(tries):
        status = _get(creation_id, {"fields": "status_code"})
        if status.get("status_code") == "FINISHED":
            return True
        if status.get("status_code") == "ERROR":
            raise MetaError(f"IG container {creation_id} errored during processing")
        time.sleep(delay)
    return True  # proceed anyway; publish will surface a hard error if truly not ready


def post_instagram(image_url: str, caption: str, hashtags: str) -> str:
    """Publish an IG feed post, tag location (best effort), then comment hashtags.

    Returns the published media id. Hashtags go in the FIRST COMMENT -- the
    caption itself stays clean.
    """
    iid = _ig_id()
    container = {"image_url": image_url, "caption": caption}
    loc = _find_ig_location_id()
    if loc:
        container["location_id"] = loc
    try:
        created = _post(f"{iid}/media", container)
    except MetaError as exc:
        if loc:  # location may be the culprit -- retry without it
            print(f"[meta_client] IG container with location failed, retrying untagged: {exc}")
            created = _post(f"{iid}/media", {"image_url": image_url, "caption": caption})
        else:
            raise
    creation_id = created["id"]
    _wait_container_ready(creation_id)
    published = _post(f"{iid}/media_publish", {"creation_id": creation_id})
    media_id = published["id"]

    # First comment: hashtags.
    if hashtags:
        try:
            _post(f"{media_id}/comments", {"message": hashtags})
        except MetaError as exc:
            print(f"[meta_client] IG hashtag comment failed (feed post still live): {exc}")
    return media_id


def post_instagram_story(image_url: str) -> str:
    """Auto-repost the same image to the Instagram Story."""
    iid = _ig_id()
    created = _post(f"{iid}/media", {"image_url": image_url, "media_type": "STORIES"})
    creation_id = created["id"]
    _wait_container_ready(creation_id)
    published = _post(f"{iid}/media_publish", {"creation_id": creation_id})
    return published["id"]


# ---------------------------------------------------------------------------
# Real post history (voice anchor for caption generation)
# ---------------------------------------------------------------------------
def recent_page_posts(limit=6):
    """Best-effort pull of the Page's own recent post captions, for voice
    matching. Returns [] on any failure -- must never block generation."""
    try:
        pid = _page_id()
        res = _get(f"{pid}/posts", {"fields": "message", "limit": limit})
        return [p["message"] for p in res.get("data", []) if p.get("message")]
    except Exception as exc:
        print(f"[meta_client] could not pull recent page posts: {exc}")
        return []


# ---------------------------------------------------------------------------
# Token expiry (for the 60-day reminder)
# ---------------------------------------------------------------------------
def days_until_token_expires():
    """Return whole days left on the current token, or None if it can't be read."""
    try:
        res = _get("debug_token", {"input_token": _token()})
        expires_at = res.get("data", {}).get("expires_at")
        if not expires_at:  # 0 means "never" (some system tokens)
            return None
        return int((expires_at - time.time()) // 86400)
    except Exception as exc:
        print(f"[meta_client] could not check token expiry: {exc}")
        return None
