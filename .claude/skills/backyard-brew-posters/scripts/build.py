#!/usr/bin/env python3
"""Backyard Brew poster pipeline: crop, embed fonts, render.

Run from the working directory holding Main.dc.html / Social.dc.html and the
image assets.

    python build.py crop wide_market.jpg market-hero.jpg --box 1500,900,3750,3900
    python build.py specimen "MARKET & BREWS" --faces LilitaOne,TitanOne,AlfaSlabOne-Regular
    python build.py build --display LilitaOne

`build` embeds the fonts into every *.dc.html (replacing the /*@FONTS@*/
marker in the helmet <style>), writes a standalone preview per artboard with
the images inlined, and renders each to PNG at its real size.

Artboard sizes come from the $preview in each file's data-props, so a resized
artboard needs no change here.
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, os.pardir, "assets", "fonts")
IMAGE_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
              ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml"}


def chrome():
    for p in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
    ):
        if p and os.path.exists(p):
            return p
    sys.exit("no Chrome found — install it or render another way")


def shot(html_path, png_path, w, h):
    """Headless screenshot. --screenshot needs an absolute path or it fails
    with 'Access is denied' and writes nothing."""
    subprocess.run([
        chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={w},{h}",
        "--screenshot=" + os.path.abspath(png_path),
        "file:///" + os.path.abspath(html_path).replace("\\", "/"),
    ], check=True, capture_output=True)
    if not os.path.exists(png_path):
        sys.exit(f"chrome wrote nothing to {png_path}")


def b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


DISPLAY_FAMILY = {
    "LilitaOne": "Lilita One",
    "TitanOne": "Titan One",
    "AlfaSlabOne-Regular": "Alfa Slab One",
    "Anton-Regular": "Anton",
    "Shrikhand-Regular": "Shrikhand",
    "BarlowCondensed-Bold": "Barlow Condensed",
}


def font_css(display):
    """Display face + both Barlow weights, as data URIs. Linked webfonts do
    not survive PNG/PDF export, which is the whole reason for embedding."""
    family = DISPLAY_FAMILY.get(display)
    if family is None:
        sys.exit("unknown display font %r — add it to DISPLAY_FAMILY and assets/fonts" % display)
    faces = [(family, display + ".ttf", 400)]
    faces += [("Barlow Condensed", "BarlowCondensed-Medium.ttf", 500),
              ("Barlow Condensed", "BarlowCondensed-Bold.ttf", 700)]
    out = []
    for family, filename, weight in faces:
        path = os.path.join(FONT_DIR, filename)
        if not os.path.exists(path):
            sys.exit(f"missing font {path}")
        out.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:%d;"
            "font-display:block;src:url(data:font/ttf;base64,%s) format('truetype');}"
            % (family, weight, b64(path))
        )
    return "\n    ".join(out)


def artboard_size(src):
    m = re.search(r"data-props='([^']*)'", src)
    if m:
        try:
            pv = json.loads(m.group(1).replace("&amp;", "&").replace("&#39;", "'")).get("$preview")
            if pv:
                return int(pv["width"]), int(pv["height"])
        except (ValueError, KeyError):
            pass
    m = re.search(r"width:\s*(\d+)px;\s*height:\s*(\d+)px", src)
    if not m:
        sys.exit(f"cannot determine artboard size for {src[:40]}...")
    return int(m.group(1)), int(m.group(2))


def cmd_crop(a):
    from PIL import Image
    im = Image.open(a.src)
    if a.box:
        im = im.crop(tuple(int(v) for v in a.box.split(",")))
    w = a.width
    h = int(round(w / a.ratio))
    im.resize((w, h), Image.LANCZOS).save(a.out, quality=a.quality, optimize=True, progressive=True)
    print(f"{a.out}  {w}x{h}  {os.path.getsize(a.out)} bytes")


def cmd_specimen(a):
    faces = a.faces.split(",")
    css, rows = [], []
    for name in faces:
        path = os.path.join(FONT_DIR, name + ".ttf")
        if not os.path.exists(path):
            sys.exit(f"missing font {path}")
        css.append("@font-face{font-family:'%s';src:url(data:font/ttf;base64,%s) format('truetype');}"
                   % (name, b64(path)))
        rows.append(
            '<div style="padding:30px 44px;border-bottom:1px solid #1e364d">'
            '<div style="font:700 20px sans-serif;letter-spacing:.3em;color:#C8922A;'
            'text-transform:uppercase;margin-bottom:10px">%s</div>'
            '<div style="font-family:\'%s\';font-size:%dpx;color:#F5C842;line-height:1.02">%s</div>'
            "</div>" % (name, name, a.size, a.text)
        )
    html = ("<!doctype html><meta charset=utf-8><style>%s\nbody{margin:0;background:#0B1C2D;width:%dpx}"
            "</style>%s" % ("\n".join(css), a.width, "".join(rows)))
    tmp = "_specimen.html"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(html)
    shot(tmp, a.out, a.width, 260 * len(faces))
    os.remove(tmp)
    print(f"{a.out} — look at it, then pick")


def cmd_build(a):
    css = font_css(a.display)
    for name in sorted(f for f in os.listdir(".") if f.endswith(".dc.html")):
        with open(name, encoding="utf-8") as fh:
            src = fh.read()
        if "/*@FONTS@*/" in src:
            src = src.replace("/*@FONTS@*/", css)
            with open(name, "w", encoding="utf-8") as fh:
                fh.write(src)
        style = re.search(r"<helmet>\s*<style>(.*?)</style>\s*</helmet>", src, re.S)
        if not style:
            sys.exit(f"{name}: no <helmet><style> block")
        body = src.split("</helmet>", 1)[1].split("</x-dc>")[0]
        for asset in os.listdir("."):
            ext = os.path.splitext(asset)[1].lower()
            if ext in IMAGE_MIME and '"%s"' % asset in body:
                body = body.replace('"%s"' % asset,
                                    '"data:%s;base64,%s"' % (IMAGE_MIME[ext], b64(asset)))
        w, h = artboard_size(src)
        stem = name[: -len(".dc.html")]
        preview = "_preview_%s.html" % stem.lower()
        with open(preview, "w", encoding="utf-8") as fh:
            fh.write('<!doctype html><meta charset="utf-8"><style>%s\n'
                     "html,body{margin:0;width:%dpx;height:%dpx;overflow:hidden}</style>%s"
                     % (style.group(1), w, h, body))
        png = "%s.png" % stem.lower()
        shot(preview, png, w, h)
        if not a.keep_previews:
            os.remove(preview)
        print(f"{png}  {w}x{h}  {os.path.getsize(png)} bytes")
    print("now LOOK at the PNGs before publishing")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("crop", help="crop and downscale a photo for full-bleed use")
    c.add_argument("src")
    c.add_argument("out")
    c.add_argument("--box", help="x1,y1,x2,y2 in the ORIGINAL image's pixels")
    c.add_argument("--ratio", type=float, default=0.75, help="width/height, default 3:4")
    c.add_argument("--width", type=int, default=1215)
    c.add_argument("--quality", type=int, default=72)
    c.set_defaults(func=cmd_crop)

    s = sub.add_parser("specimen", help="render candidate display faces to compare")
    s.add_argument("text")
    s.add_argument("--faces", default="LilitaOne,TitanOne,AlfaSlabOne-Regular")
    s.add_argument("--size", type=int, default=88)
    s.add_argument("--width", type=int, default=1100)
    s.add_argument("--out", default="specimen.png")
    s.set_defaults(func=cmd_specimen)

    b = sub.add_parser("build", help="embed fonts, inline images, render every artboard")
    b.add_argument("--display", default="LilitaOne", help="display font file stem in assets/fonts")
    b.add_argument("--keep-previews", action="store_true")
    b.set_defaults(func=cmd_build)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
