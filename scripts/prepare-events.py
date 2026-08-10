"""Prepare event photos from archive into images/evenements/{slug}/photo-NN.webp."""
from pathlib import Path
from PIL import Image, ImageOps
import re
import unicodedata
import json

SRC = Path(r"A:\sites\galadhrim-dagnir-site-v2\2025-20260810T154116Z-1-001\2025")
DST = Path(r"A:\sites\galadhrim-dagnir-site-v2\images\evenements")
MAX_SIDE = 1400
QUALITY = 72

# source folder key (normalized) -> (slug, display, cover preference stems)
EVENTS = {
    "beville": ("beville-le-comte-2025", "Béville-le-Comte — Septembre 2025", ["1757844340718"]),
    "camp-off-mai": ("camp-off-mai-2025", "Camp Off — Mai 2025", ["groupe-1", "groupe 1"]),
    "camp-off-octobre": ("camp-off-octobre-2025", "Camp Off — Octobre 2025", ["1000021125"]),
    "teaudun": ("chateaudun-2025", "Châteaudun — Juillet 2025", ["chateaudun-2025", "Châteaudun 2025"]),
    "cidre": ("cidre-et-dragon-2025", "Cidre et Dragon — Septembre 2025", ["1000017555"]),
    "dinan": ("dinan-2025", "Dinan — Juillet 2025", ["1000014110"]),
    "galardon": ("galardon-2025", "Galardon — Mai 2025", ["1753051352116"]),
    "rodemack": ("rodemack-2025", "Rodemack — Juin 2025", ["1000012756"]),
    "plestin": ("plestin-2024", "Sur les Terres de l'Unique — Plestin, Septembre 2024", ["1753051673246"]),
    "unique": ("plestin-2024", "Sur les Terres de l'Unique — Plestin, Septembre 2024", ["1753051673246"]),
}

ORDER = [
    "camp-off-octobre-2025",
    "beville-le-comte-2025",
    "cidre-et-dragon-2025",
    "chateaudun-2025",
    "dinan-2025",
    "rodemack-2025",
    "camp-off-mai-2025",
    "galardon-2025",
    "plestin-2024",
]


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("'", "").replace("’", "").replace("_", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def match_event(folder_name: str):
    slug_key = slugify(folder_name)
    for key, meta in EVENTS.items():
        if key in slug_key:
            return meta
    return None


def process_image(src_path: Path, dest_path: Path) -> bool:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(src_path) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "P", "LA"):
                im = im.convert("RGB")
            elif im.mode != "RGB":
                im = im.convert("RGB")
            w, h = im.size
            scale = min(1.0, MAX_SIDE / max(w, h))
            if scale < 1.0:
                im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            im.save(dest_path, "WEBP", quality=QUALITY, method=6)
            return True
    except Exception as e:
        print(f"FAIL {src_path}: {e}")
        return False


def main() -> None:
    folders = [p for p in SRC.iterdir() if p.is_dir()]
    events_meta = []
    seen_slugs = set()

    for folder in folders:
        meta = match_event(folder.name)
        if not meta:
            print(f"SKIP unknown folder: {folder.name!r}")
            continue
        slug, display, prefer = meta
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        files = sorted(
            [
                p
                for p in folder.rglob("*")
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
            ],
            key=lambda p: str(p).lower(),
        )

        cover_src = None
        for pref in prefer:
            pref_slug = slugify(pref)
            for f in files:
                if slugify(f.stem) == pref_slug or f.stem.startswith(pref):
                    cover_src = f
                    break
            if cover_src:
                break
        if cover_src is None and files:
            cover_src = files[0]

        ordered = []
        if cover_src:
            ordered.append(cover_src)
        for f in files:
            if f != cover_src:
                ordered.append(f)

        out_dir = DST / slug
        if out_dir.exists():
            for p in out_dir.glob("*"):
                p.unlink()
        out_dir.mkdir(parents=True, exist_ok=True)

        images = []
        for i, src in enumerate(ordered, start=1):
            name = f"photo-{i:02d}.webp"
            if process_image(src, out_dir / name):
                images.append(name)

        events_meta.append(
            {
                "slug": slug,
                "name": display,
                "cover": images[0] if images else None,
                "images": images,
                "count": len(images),
                "source": folder.name,
            }
        )
        print(f"OK {slug}: {len(images)} images")

    order_index = {s: i for i, s in enumerate(ORDER)}
    events_meta.sort(key=lambda e: order_index.get(e["slug"], 99))
    manifest = DST / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(events_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", manifest)
    total = sum(p.stat().st_size for p in DST.rglob("*.webp"))
    print(f"Total output size: {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
