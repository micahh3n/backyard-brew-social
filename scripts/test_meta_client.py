from unittest.mock import patch

import meta_client


def test_recent_page_posts_returns_messages_only():
    fake_response = {"data": [{"message": "Bingo's back!"}, {"id": "123"}, {"message": "Poker night."}]}
    with patch("meta_client._page_id", return_value="123"), \
         patch("meta_client._get", return_value=fake_response):
        result = meta_client.recent_page_posts(limit=6)
    assert result == ["Bingo's back!", "Poker night."]


def test_recent_page_posts_returns_empty_on_failure():
    with patch("meta_client._get", side_effect=meta_client.MetaError("boom")):
        result = meta_client.recent_page_posts(limit=6)
    assert result == []


def test_post_instagram_carousel_builds_children_then_publishes():
    calls = []

    def fake_post(path, data):
        calls.append((path, data))
        if path.endswith("/media") and data.get("is_carousel_item"):
            return {"id": f"child-{len(calls)}"}
        if path.endswith("/media") and data.get("media_type") == "CAROUSEL":
            return {"id": "parent-container"}
        if path.endswith("/media_publish"):
            return {"id": "published-123"}
        if path.endswith("/comments"):
            return {"id": "comment-1"}
        raise AssertionError(f"unexpected path {path}")

    with patch("meta_client._post", side_effect=fake_post), \
         patch("meta_client._get", return_value={"status_code": "FINISHED"}), \
         patch("meta_client._ig_id", return_value="ig123"), \
         patch("meta_client._find_ig_location_id", return_value=None):
        result = meta_client.post_instagram_carousel(
            ["https://x/1.jpg", "https://x/2.jpg", "https://x/3.jpg"], "caption", "#tags")

    assert result == "published-123"
    child_calls = [c for c in calls if c[1].get("is_carousel_item")]
    assert len(child_calls) == 3


def test_post_instagram_carousel_rejects_fewer_than_two_photos():
    with patch("meta_client._post") as mock_post, \
         patch("meta_client._ig_id", return_value="ig123"):
        try:
            meta_client.post_instagram_carousel(["https://x/only-one.jpg"], "caption", "#tags")
            assert False, "expected MetaError to be raised"
        except meta_client.MetaError:
            pass
    mock_post.assert_not_called()


def test_post_facebook_multi_uploads_unpublished_then_posts():
    calls = []

    def fake_post(path, data):
        calls.append((path, data))
        if path.endswith("/photos"):
            return {"id": f"photo-{len(calls)}"}
        if path.endswith("/feed"):
            return {"id": "feed-post-1"}
        raise AssertionError(f"unexpected path {path}")

    with patch("meta_client._post", side_effect=fake_post), \
         patch("meta_client._page_id", return_value="page123"):
        result = meta_client.post_facebook_multi(["https://x/1.jpg", "https://x/2.jpg"], "caption")

    assert result == "feed-post-1"
    photo_calls = [c for c in calls if c[0].endswith("/photos")]
    assert len(photo_calls) == 2
    assert all(c[1].get("published") == "false" for c in photo_calls)
