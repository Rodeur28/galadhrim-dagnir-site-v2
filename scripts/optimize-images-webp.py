"""Convert all site images to optimized WebP and rewrite references."""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(r"A:\sites\galadhrim-dagnir-site-v2")
IMG_ROOT = ROOT / "images"
QUALITY = 80
MAX_SIDE = 1600
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def dest_webp(path: Path) -> Path:
    return path.with_suffix(".webp")


def optimize_to_webp(src: Path, dest: Path) -> tuple[int, int]:
    """Returns (src_bytes, dest_bytes)."""
    src_size = src.stat().st_size
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
            im = im.convert("RGBA")
        elif im.mode != "RGB":
            im = im.convert("RGB")

        w, h = im.size
        scale = min(1.0, MAX_SIDE / max(w, h))
        if scale < 1.0:
            im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)

        # Write to temp then keep only if smaller / equal for same-format recompress
        tmp = dest.with_suffix(".webp.tmp")
        save_kwargs = {"quality": QUALITY, "method": 6}
        if im.mode == "RGBA":
            save_kwargs["lossless"] = False
        im.save(tmp, "WEBP", **save_kwargs)
        dest_size = tmp.stat().st_size

        if src.suffix.lower() == ".webp" and dest.resolve() == src.resolve():
            # Recompress in place: keep smaller
            if dest_size < src_size:
                tmp.replace(dest)
                return src_size, dest_size
            tmp.unlink(missing_ok=True)
            return src_size, src_size

        tmp.replace(dest)
        return src_size, dest_size


def collect_images() -> list[Path]:
    files = []
    for p in IMG_ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            files.append(p)
    return sorted(files)


def rewrite_text_files(replacements: list[tuple[str, str]]) -> int:
    """Replace path strings in site text files. replacements: (old, new) relative paths with forward slashes."""
    # Sort longest first to avoid partial overlaps
    replacements = sorted(replacements, key=lambda x: len(x[0]), reverse=True)
    text_exts = {".html", ".css", ".js", ".xml", ".json", ".md", ".txt"}
    updated = 0
    skip_dirs = {
        "2025-20260810T154116Z-1-001",
        ".git",
        "node_modules",
        "scripts",
    }

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in text_exts:
            continue
        # Skip binary-ish
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        original = text
        for old, new in replacements:
            if old in text:
                text = text.replace(old, new)
            # Also handle Windows backslash variants if any
            old_bs = old.replace("/", "\\")
            if old_bs in text:
                text = text.replace(old_bs, new.replace("/", "\\"))

        # Generic extension swap for remaining jpg refs under images/
        text2 = re.sub(
            r"(images/[^\"'\s<>]+\.)(?:jpe?g|png|JPG|JPEG|PNG)",
            lambda m: m.group(1) + "webp",
            text,
            flags=re.IGNORECASE,
        )
        text = text2

        if text != original:
            path.write_text(text, encoding="utf-8")
            updated += 1
            print(f"  updated refs: {path.relative_to(ROOT)}")
    return updated


def update_manifest() -> None:
    manifest = IMG_ROOT / "events" / "manifest.json"
    if not manifest.exists():
        return
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for e in data:
        if e.get("cover"):
            e["cover"] = Path(e["cover"]).with_suffix(".webp").name
        e["images"] = [Path(n).with_suffix(".webp").name for n in e.get("images", [])]
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Updated manifest.json")


def main() -> None:
    images = collect_images()
    print(f"Found {len(images)} images")

    before = sum(p.stat().st_size for p in images)
    replacements: list[tuple[str, str]] = []
    to_delete: list[Path] = []
    converted = 0
    recompressed = 0
    after_total = 0

    for src in images:
        rel = src.relative_to(ROOT).as_posix()
        dest = dest_webp(src)
        dest_rel = dest.relative_to(ROOT).as_posix()

        src_size, dest_size = optimize_to_webp(src, dest)
        after_total += dest_size

        if src.suffix.lower() != ".webp":
            replacements.append((rel, dest_rel))
            # Also relative without leading path variants used in HTML
            # e.g. images/foo.JPG vs Images/...
            replacements.append((rel.replace("images/", "images/"), dest_rel))
            to_delete.append(src)
            converted += 1
            print(f"  JPG/PNG->WebP {rel} ({src_size/1024:.0f}->{dest_size/1024:.0f} KB)")
        else:
            if dest_size < src_size:
                recompressed += 1
                print(f"  recompress {rel} ({src_size/1024:.0f}->{dest_size/1024:.0f} KB)")

    print(f"\nConverted: {converted}, recompressed: {recompressed}")
    print(f"Size before: {before/1e6:.1f} MB")

    print("\nRewriting references...")
    n = rewrite_text_files(replacements)
    print(f"Files with refs updated: {n}")

    update_manifest()

    print("\nDeleting original JPG/PNG...")
    deleted = 0
    freed = 0
    for p in to_delete:
        if p.exists() and p.suffix.lower() != ".webp":
            freed += p.stat().st_size
            p.unlink()
            deleted += 1
    print(f"Deleted {deleted} files ({freed/1e6:.1f} MB)")

    remaining = [p for p in IMG_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in IMG_EXTS]
    final = sum(p.stat().st_size for p in remaining)
    print(f"\nFinal images: {len(remaining)} files, {final/1e6:.1f} MB (was {before/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
