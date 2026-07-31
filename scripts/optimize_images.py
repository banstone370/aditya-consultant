"""Optimize website images: resize and compress for faster loading."""
from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "img"
ICON = IMG / "icon"

MAX_DIMENSION = 1600
JPEG_QUALITY = 82
LOGO_MAX = 512

KEEP_PNG = {"Adity_Consultant_Logo.png"}
CONVERTED: dict[str, str] = {}


def resize_if_needed(img: Image.Image, max_dim: int) -> Image.Image:
    w, h = img.size
    if max(w, h) <= max_dim:
        return img
    scale = max_dim / max(w, h)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def save_jpeg(img: Image.Image, dest: Path) -> None:
    rgb = img.convert("RGB")
    rgb.save(
        dest,
        "JPEG",
        quality=JPEG_QUALITY,
        optimize=True,
        progressive=True,
    )


def optimize_logo(path: Path) -> None:
    before = path.stat().st_size
    with Image.open(path) as img:
        img = resize_if_needed(img, LOGO_MAX)
        img.save(path, "PNG", optimize=True, compress_level=9)
    after = path.stat().st_size
    print(f"  logo {path.name}: {before/1024:.0f}KB -> {after/1024:.0f}KB")


def optimize_icon(path: Path) -> None:
    before = path.stat().st_size
    with Image.open(path) as img:
        if img.mode not in ("RGBA", "RGB", "P"):
            img = img.convert("RGBA")
        img.save(path, "PNG", optimize=True, compress_level=9)
    after = path.stat().st_size
    if before > after:
        print(f"  icon {path.name}: {before/1024:.0f}KB -> {after/1024:.0f}KB")


def convert_photo_png(path: Path) -> None:
    before = path.stat().st_size
    dest = path.with_suffix(".jpg")
    with Image.open(path) as img:
        img = resize_if_needed(img, MAX_DIMENSION)
        save_jpeg(img, dest)
    path.unlink()
    after = dest.stat().st_size
    CONVERTED[path.name] = dest.name
    print(f"  {path.name} -> {dest.name}: {before/1024/1024:.2f}MB -> {after/1024:.0f}KB")


def optimize_jpeg(path: Path) -> None:
    before = path.stat().st_size
    with Image.open(path) as img:
        img = resize_if_needed(img, MAX_DIMENSION)
        save_jpeg(img, path)
    after = path.stat().st_size
    print(f"  jpeg {path.name}: {before/1024:.0f}KB -> {after/1024:.0f}KB")


def update_references() -> None:
    if not CONVERTED:
        return
    patterns = [
        (re.compile(re.escape(old)), new)
        for old, new in CONVERTED.items()
    ]
    for file in ROOT.rglob("*"):
        if file.suffix.lower() not in {".html", ".css", ".js"}:
            continue
        text = file.read_text(encoding="utf-8", errors="replace")
        original = text
        for pattern, new in patterns:
            text = pattern.sub(new, text)
        if text != original:
            file.write_text(text, encoding="utf-8")
            print(f"  updated refs in {file.relative_to(ROOT)}")


def folder_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def main() -> None:
    before_total = folder_size(IMG)
    print(f"img folder before: {before_total/1024/1024:.1f} MB\n")

    print("Converting photo PNGs to JPEG...")
    for path in sorted(IMG.glob("*.png")):
        if path.name in KEEP_PNG:
            continue
        convert_photo_png(path)

    print("\nOptimizing logo...")
    optimize_logo(IMG / "Adity_Consultant_Logo.png")

    print("\nOptimizing icons...")
    for path in sorted(ICON.glob("*.png")):
        optimize_icon(path)

    print("\nOptimizing JPEGs...")
    for path in sorted(IMG.glob("*.jpg")):
        optimize_jpeg(path)
    for path in sorted(IMG.glob("*.jpe")):
        optimize_jpeg(path)

    print("\nUpdating HTML/CSS/JS references...")
    update_references()

    after_total = folder_size(IMG)
    saved = before_total - after_total
    print(f"\nimg folder after: {after_total/1024/1024:.1f} MB")
    print(f"saved: {saved/1024/1024:.1f} MB ({100*saved/before_total:.0f}% reduction)")


if __name__ == "__main__":
    main()
