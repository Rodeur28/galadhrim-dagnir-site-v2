"""Rename event folders/images and top-level assets to clean WebP names."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"A:\sites\galadhrim-dagnir-site-v2")
IMG = ROOT / "images"
OLD_EVENTS = IMG / "events"
NEW_EVENTS = IMG / "evenements"

# Old folder slug -> new folder slug
FOLDER_MAP = {
    "camp-off-octobre-2025": "camp-off-octobre-2025",
    "beville-le-conte-sept-2025": "beville-le-comte-2025",
    "cidre-et-dragon-sept-2025": "cidre-et-dragon-2025",
    "chateaudun-juillet-2025": "chateaudun-2025",
    "dinan-juillet-2025": "dinan-2025",
    "rodemack-juin-2025": "rodemack-2025",
    "camp-off-mai-2025": "camp-off-mai-2025",
    "galardon-mai-2025": "galardon-2025",
    "sur-les-terres-de-l-unique-plestin-septembre-2024": "plestin-2024",
}

DISPLAY = {
    "camp-off-octobre-2025": "Camp Off — Octobre 2025",
    "beville-le-comte-2025": "Béville-le-Comte — Septembre 2025",
    "cidre-et-dragon-2025": "Cidre et Dragon — Septembre 2025",
    "chateaudun-2025": "Châteaudun — Juillet 2025",
    "dinan-2025": "Dinan — Juillet 2025",
    "rodemack-2025": "Rodemack — Juin 2025",
    "camp-off-mai-2025": "Camp Off — Mai 2025",
    "galardon-2025": "Galardon — Mai 2025",
    "plestin-2024": "Sur les Terres de l'Unique — Plestin, Septembre 2024",
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

# Preferred cover stems (without extension) per old folder, matched against old filenames
COVER_PREFER = {
    "camp-off-octobre-2025": ["1000021125"],
    "beville-le-conte-sept-2025": ["1757844340718"],
    "cidre-et-dragon-sept-2025": ["1000017555"],
    "chateaudun-juillet-2025": ["chateaudun-2025"],
    "dinan-juillet-2025": ["1000014110"],
    "rodemack-juin-2025": ["1000012756"],
    "camp-off-mai-2025": ["groupe-1"],
    "galardon-mai-2025": ["1753051352116"],
    "sur-les-terres-de-l-unique-plestin-septembre-2024": ["1753051673246"],
}

TOP_LEVEL_RENAMES = {
    "activites2026.webp": "activites-2026.webp",
    "besacegondor.webp": "besace-gondor.webp",
    "groupe1.webp": "groupe-1.webp",
    "groupe3.webp": "groupe-3.webp",
    "groupe5.webp": "groupe-5.webp",
    "groupe6.webp": "groupe-6.webp",
    "groupe7.webp": "groupe-7.webp",
    "groupe8.webp": "groupe-8.webp",
    "groupe10.webp": "groupe-10.webp",
    "groupe11.webp": "groupe-11.webp",
    "camp16.webp": "camp-16.webp",
    "camp32.webp": "camp-32.webp",
    "guerillarodeur.webp": "guerilla-rodeur.webp",
    "rodeurface.webp": "rodeur-face.webp",
    "rodeurlance.webp": "rodeur-lance.webp",
    "hierarchie-grades-sombrehierarchie-grades-sombre.webp": "hierarchie-grades-sombre.webp",
    "Kaem.webp": "kaem.webp",
    "tenue-apparat-v3.webp": "tenue-apparat.webp",
    "tenue-sables-def.webp": "tenue-sables.webp",
}


def needs_clean_name(name: str) -> bool:
    stem = Path(name).stem
    if re.fullmatch(r"\d{8,}", stem):
        return True
    if re.fullmatch(r"\d{6,}", stem):
        return True
    if re.search(r"\d{10,}", stem):
        return True
    if "-n" in stem and re.search(r"\d{8,}", stem):
        return True
    if stem.startswith("chatgpt-"):
        return True
    if "scaled" in stem:
        return True
    if len(stem) > 40:
        return True
    return False


def rename_path(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if src.resolve() == dest.resolve():
            return
        dest.unlink()
    src.rename(dest)


def process_events() -> list[dict]:
    if not OLD_EVENTS.exists() and NEW_EVENTS.exists():
        events_root = NEW_EVENTS
        # Already moved; rebuild from current structure
        old_manifest = NEW_EVENTS / "manifest.json"
    else:
        events_root = OLD_EVENTS

    old_manifest_path = events_root / "manifest.json"
    old_data = json.loads(old_manifest_path.read_text(encoding="utf-8")) if old_manifest_path.exists() else []
    by_old_slug = {e["slug"]: e for e in old_data}

    # Stage into a temp dir then swap, to avoid collisions
    staging = IMG / "_evenements_staging"
    if staging.exists():
        for p in sorted(staging.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            else:
                p.rmdir()
        staging.rmdir()
    staging.mkdir(parents=True)

    new_events: list[dict] = []
    path_replacements: list[tuple[str, str]] = []

    for old_slug, new_slug in FOLDER_MAP.items():
        src_dir = events_root / old_slug
        if not src_dir.exists():
            # maybe already renamed
            src_dir = events_root / new_slug
        if not src_dir.exists():
            print(f"MISSING {old_slug}")
            continue

        files = sorted([p for p in src_dir.glob("*.webp")], key=lambda p: p.name.lower())
        prefer = COVER_PREFER.get(old_slug, [])
        cover_src = None
        for pref in prefer:
            for f in files:
                if f.stem == pref or f.stem.startswith(pref):
                    cover_src = f
                    break
            if cover_src:
                break
        if cover_src is None and files:
            cover_src = files[0]

        # Order: cover first, then the rest in original order
        ordered = []
        if cover_src:
            ordered.append(cover_src)
        for f in files:
            if f != cover_src:
                ordered.append(f)

        dest_dir = staging / new_slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        image_names = []
        for i, src in enumerate(ordered, start=1):
            new_name = f"photo-{i:02d}.webp"
            dest = dest_dir / new_name
            # copy via rename from a temp duplicate? We need to keep source until all done
            # Use read/write bytes to avoid cross-device issues, or rename after staging copy
            dest.write_bytes(src.read_bytes())
            image_names.append(new_name)

            old_rel = f"images/evenements/{old_slug}/{src.name}"
            new_rel = f"images/evenements/{new_slug}/{new_name}"
            path_replacements.append((old_rel, new_rel))
            # also if already under evenements with old names
            path_replacements.append((f"images/evenements/{old_slug}/{src.name}", new_rel))
            path_replacements.append((f"images/evenements/{new_slug}/{src.name}", new_rel))

        cover_name = image_names[0]
        new_events.append(
            {
                "slug": new_slug,
                "name": DISPLAY[new_slug],
                "cover": cover_name,
                "images": image_names,
                "count": len(image_names),
            }
        )
        print(f"OK {old_slug} -> {new_slug} ({len(image_names)} photos, cover={cover_name})")

    # Order
    order_index = {s: i for i, s in enumerate(ORDER)}
    new_events.sort(key=lambda e: order_index.get(e["slug"], 99))

    (staging / "manifest.json").write_text(
        json.dumps(new_events, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Replace old events dirs
    for target in (OLD_EVENTS, NEW_EVENTS):
        if target.exists():
            for p in sorted(target.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink()
                else:
                    p.rmdir()

    staging.rename(NEW_EVENTS)
    print(f"Events now at {NEW_EVENTS}")
    return new_events, path_replacements


def process_top_level() -> list[tuple[str, str]]:
    replacements = []
    for old_name, new_name in TOP_LEVEL_RENAMES.items():
        src = IMG / old_name
        dest = IMG / new_name
        if not src.exists():
            if dest.exists():
                print(f"skip (already) {new_name}")
            else:
                print(f"missing top-level {old_name}")
            continue
        if src.resolve() == dest.resolve():
            continue
        if dest.exists():
            dest.unlink()
        src.rename(dest)
        replacements.append((f"images/{old_name}", f"images/{new_name}"))
        print(f"TOP {old_name} -> {new_name}")
    return replacements


def rewrite_refs(replacements: list[tuple[str, str]]) -> None:
    # Also map HTML event page filenames
    html_page_map = {
        "evenements/beville-le-comte-2025.html": "evenements/beville-le-comte-2025.html",
        "evenements/cidre-et-dragon-2025.html": "evenements/cidre-et-dragon-2025.html",
        "evenements/chateaudun-2025.html": "evenements/chateaudun-2025.html",
        "evenements/dinan-2025.html": "evenements/dinan-2025.html",
        "evenements/rodemack-2025.html": "evenements/rodemack-2025.html",
        "evenements/galardon-2025.html": "evenements/galardon-2025.html",
        "evenements/plestin-2024.html": "evenements/plestin-2024.html",
    }

    all_repl = sorted(
        list(replacements) + list(html_page_map.items()) + [
            ("images/evenements/", "images/evenements/"),
        ],
        key=lambda x: len(x[0]),
        reverse=True,
    )

    skip = {".git", "2025-20260810T154116Z-1-001", "node_modules", "_evenements_staging"}
    text_exts = {".html", ".css", ".js", ".xml", ".json", ".md", ".txt", ".py"}

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(s in path.parts for s in skip):
            continue
        if path.suffix.lower() not in text_exts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        for old, new in all_repl:
            if old in text:
                text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"  refs: {path.relative_to(ROOT)}")


def rename_event_html_pages() -> None:
    events_html = ROOT / "evenements"
    renames = {
        "beville-le-conte-sept-2025.html": "beville-le-comte-2025.html",
        "cidre-et-dragon-sept-2025.html": "cidre-et-dragon-2025.html",
        "chateaudun-juillet-2025.html": "chateaudun-2025.html",
        "dinan-juillet-2025.html": "dinan-2025.html",
        "rodemack-juin-2025.html": "rodemack-2025.html",
        "galardon-mai-2025.html": "galardon-2025.html",
        "sur-les-terres-de-l-unique-plestin-septembre-2024.html": "plestin-2024.html",
    }
    for old, new in renames.items():
        src = events_html / old
        dest = events_html / new
        if src.exists():
            if dest.exists() and src.resolve() != dest.resolve():
                dest.unlink()
            src.rename(dest)
            print(f"HTML {old} -> {new}")


def regenerate_event_pages(events: list[dict]) -> None:
    """Regenerate listing + event pages with clean names."""
    import html as html_mod

    def esc(s: str) -> str:
        return html_mod.escape(s, quote=True)

    nav = """  <nav>
    <a href="{prefix}index.html">Accueil</a>
    <a href="{prefix}presentation.html">Présentation</a>
    <a href="{prefix}evenements.html">Événements</a>
    <a href="{prefix}activites.html">Activités</a>
    <a href="{prefix}rejoindre.html">Rejoindre</a>
    <a href="{prefix}contact.html">Contact</a>
    <a href="{prefix}legendes.html">Histoire & Légendes</a>
  </nav>"""
    footer = """  <footer>
    <p>© Galadhrim Dagnir – 9ème Compagnie de Rôdeurs du Gondor</p>
  </footer>"""
    lightbox = """  <div id="gd-lightbox" class="gd-lightbox" role="dialog" aria-modal="true" aria-label="Agrandissement de la photo">
    <div class="gd-lightbox-backdrop" aria-hidden="true"></div>
    <button type="button" class="gd-lightbox-close" aria-label="Fermer">×</button>
    <button type="button" class="gd-lightbox-prev" aria-label="Image précédente">‹</button>
    <button type="button" class="gd-lightbox-next" aria-label="Image suivante">›</button>
    <figure class="gd-lightbox-inner">
      <img src="" alt="">
      <figcaption></figcaption>
    </figure>
  </div>"""

    cards = []
    for e in events:
        cover = f"images/evenements/{e['slug']}/{e['cover']}"
        href = f"evenements/{e['slug']}.html"
        count_label = "1 photo" if e["count"] == 1 else f"{e['count']} photos"
        cards.append(
            f"""      <a class="event-card" href="{href}">
        <span class="event-card__media">
          <img src="{esc(cover)}" alt="" loading="lazy" width="640" height="400">
        </span>
        <span class="event-card__body">
          <span class="event-card__title">{esc(e["name"])}</span>
          <span class="event-card__meta">{count_label}</span>
        </span>
      </a>"""
        )

    og = f"https://galadhrim-dagnir.com/images/evenements/{events[0]['slug']}/{events[0]['cover']}"
    listing = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Événements – Galadhrim Dagnir</title>
  <meta name="description" content="Événements de la 9ème Compagnie de Rôdeurs Galadhrim Dagnir : camps, festivals et rencontres — photos et souvenirs." />
  <link rel="canonical" href="https://galadhrim-dagnir.com/evenements.html" />
  <meta property="og:title" content="Événements – Galadhrim Dagnir" />
  <meta property="og:description" content="Camps, festivals et rencontres des Rôdeurs du Gondor." />
  <meta property="og:image" content="{og}" />
  <meta property="og:url" content="https://galadhrim-dagnir.com/evenements.html" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="fr_FR" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="alternate" hreflang="fr" href="https://galadhrim-dagnir.com/evenements.html" />
  <link rel="alternate" hreflang="x-default" href="https://galadhrim-dagnir.com/evenements.html" />
  <link rel="stylesheet" href="css/site.css">
  <link rel="stylesheet" href="css/page-inner.css">
  <link rel="stylesheet" href="css/evenements.css">
</head>
<body class="page-inner">
{nav.format(prefix="")}

  <header class="inner-hero">
    <p class="inner-hero__eyebrow">Galadhrim Dagnir</p>
    <h1 class="inner-hero__title">Événements</h1>
    <p class="inner-hero__subtitle">Camps, festivals et rencontres — les traces de nos marches sur les chemins.</p>
  </header>

  <main class="inner-main inner-main--wide">
    <div class="verse-ornament" aria-hidden="true"></div>
    <blockquote class="verse-epigraph verse-epigraph--compact">
      <p>« Chaque feu de camp, chaque marche, chaque rencontre laisse une empreinte dans notre mémoire. »</p>
    </blockquote>
    <div class="mia-style inner-lead">
      <p>Voici les événements qui ont rassemblé la Compagnie. Choisissez une rencontre pour en parcourir les images.</p>
    </div>

    <div class="event-grid">
{chr(10).join(cards)}
    </div>
  </main>

{footer}
</body>
</html>
"""
    (ROOT / "evenements.html").write_text(listing, encoding="utf-8")

    out_dir = ROOT / "evenements"
    out_dir.mkdir(exist_ok=True)
    # remove obsolete html pages
    for old in out_dir.glob("*.html"):
        old.unlink()

    for e in events:
        imgs = []
        for name in e["images"]:
            src = f"../images/evenements/{e['slug']}/{name}"
            alt = esc(e["name"])
            imgs.append(f'      <a href="{esc(src)}"><img src="{esc(src)}" alt="{alt}" loading="lazy"></a>')
        cover = f"https://galadhrim-dagnir.com/images/evenements/{e['slug']}/{e['cover']}"
        count_label = "1 photo" if e["count"] == 1 else f"{e['count']} photos"
        page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(e["name"])} – Galadhrim Dagnir</title>
  <meta name="description" content="Galerie photos : {esc(e['name'])} — Galadhrim Dagnir, 9ème Compagnie de Rôdeurs du Gondor." />
  <link rel="canonical" href="https://galadhrim-dagnir.com/evenements/{e['slug']}.html" />
  <meta property="og:title" content="{esc(e["name"])} – Galadhrim Dagnir" />
  <meta property="og:description" content="Photos de l’événement {esc(e["name"])}." />
  <meta property="og:image" content="{cover}" />
  <meta property="og:url" content="https://galadhrim-dagnir.com/evenements/{e['slug']}.html" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="fr_FR" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="stylesheet" href="../css/site.css">
  <link rel="stylesheet" href="../css/page-inner.css">
  <link rel="stylesheet" href="../css/galerie.css">
  <link rel="stylesheet" href="../css/evenements.css">
</head>
<body class="page-inner">
{nav.format(prefix="../")}

  <header class="inner-hero">
    <p class="inner-hero__eyebrow"><a class="event-back" href="../evenements.html">← Événements</a></p>
    <h1 class="inner-hero__title">{esc(e["name"])}</h1>
    <p class="inner-hero__subtitle">{count_label}</p>
  </header>

  <main class="inner-main inner-main--wide">
    <div class="gallery gallery--masonry">
{chr(10).join(imgs)}
    </div>
  </main>

{lightbox}

{footer}

  <script src="../js/gallery-lightbox.js"></script>
</body>
</html>
"""
        (out_dir / f"{e['slug']}.html").write_text(page, encoding="utf-8")
        print(f"page {e['slug']}.html")


def update_sitemap(events: list[dict]) -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    # Replace event URL block
    event_urls = ['  <url>\n    <loc>https://galadhrim-dagnir.com/evenements.html</loc>\n  </url>']
    for e in events:
        event_urls.append(
            f"  <url>\n    <loc>https://galadhrim-dagnir.com/evenements/{e['slug']}.html</loc>\n  </url>"
        )
    block = "\n".join(event_urls)

    # Remove old event urls and insert new ones after presentation block... simpler: regex replace from evenements.html through last evenements/ url
    pattern = re.compile(
        r"  <url>\n    <loc>https://galadhrim-dagnir.com/evenements\.html</loc>\n  </url>"
        r"(?:\n  <url>\n    <loc>https://galadhrim-dagnir.com/evenements/[^<]+</loc>\n  </url>)*",
        re.MULTILINE,
    )
    if pattern.search(text):
        text = pattern.sub(block, text, count=1)
    else:
        # fallback insert before activites
        text = text.replace(
            "  <url>\n    <loc>https://galadhrim-dagnir.com/activites.html</loc>",
            block + "\n  <url>\n    <loc>https://galadhrim-dagnir.com/activites.html</loc>",
        )
    sitemap.write_text(text, encoding="utf-8")
    print("Updated sitemap.xml")


def main() -> None:
    events, event_repls = process_events()
    top_repls = process_top_level()
    rewrite_refs(event_repls + top_repls)
    regenerate_event_pages(events)
    update_sitemap(events)
    print("\nDone.")


if __name__ == "__main__":
    main()
