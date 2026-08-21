"""Filter event photos to keep-only list, renumber, regenerate pages."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(r"A:\sites\galadhrim-dagnir-site-v2")
EVENTS_IMG = ROOT / "images" / "evenements"
EVENTS_HTML = ROOT / "evenements"

KEEP = {
    "camp-off-octobre-2025": ["photo-19.webp"],
    "cidre-et-dragon-2025": [
        "photo-03.webp",
        "photo-05.webp",
        "photo-15.webp",
        "photo-16.webp",
        "photo-17.webp",
        "photo-18.webp",
        "photo-19.webp",
        "photo-20.webp",
        "photo-25.webp",
        "photo-29.webp",
    ],
    "rodemack-2025": ["photo-01.webp", "photo-06.webp", "photo-19.webp"],
    "chateaudun-2025": ["photo-01.webp"],
    "dinan-2025": ["photo-11.webp"],
    "camp-off-mai-2025": [
        "photo-03.webp",
        "photo-04.webp",
        "photo-08.webp",
        "photo-10.webp",
        "photo-39.webp",
        "photo-42.webp",
        "photo-59.webp",
        "photo-60.webp",
        "photo-71.webp",
    ],
    # empty -> remove event entirely
    "beville-le-comte-2025": [],
    "galardon-2025": [],
    "plestin-2024": [],
}

DISPLAY = {
    "camp-off-octobre-2025": "Camp Off — Octobre 2025",
    "cidre-et-dragon-2025": "Cidre et Dragon — Septembre 2025",
    "rodemack-2025": "Rodemack — Juin 2025",
    "chateaudun-2025": "Châteaudun — Juillet 2025",
    "dinan-2025": "Dinan — Juillet 2025",
    "camp-off-mai-2025": "Camp Off — Mai 2025",
}

ORDER = [
    "camp-off-octobre-2025",
    "cidre-et-dragon-2025",
    "chateaudun-2025",
    "dinan-2025",
    "rodemack-2025",
    "camp-off-mai-2025",
]


def filter_and_renumber() -> list[dict]:
    events_meta = []
    for slug in list(KEEP.keys()):
        folder = EVENTS_IMG / slug
        keep_files = KEEP[slug]

        if not keep_files:
            if folder.exists():
                shutil.rmtree(folder)
                print(f"REMOVED event folder {slug}")
            html = EVENTS_HTML / f"{slug}.html"
            if html.exists():
                html.unlink()
                print(f"REMOVED page {slug}.html")
            continue

        if not folder.exists():
            print(f"MISSING {slug}")
            continue

        # Stage kept files
        staging = folder / "_keep"
        staging.mkdir(exist_ok=True)
        new_names = []
        for i, name in enumerate(keep_files, start=1):
            src = folder / name
            if not src.exists():
                print(f"  WARN missing keep file {slug}/{name}")
                continue
            new_name = f"photo-{i:02d}.webp"
            dest = staging / new_name
            shutil.copy2(src, dest)
            new_names.append(new_name)

        # Delete all old photos in folder (not staging)
        for p in folder.glob("photo-*.webp"):
            p.unlink()

        for p in staging.glob("*.webp"):
            p.rename(folder / p.name)
        staging.rmdir()

        events_meta.append(
            {
                "slug": slug,
                "name": DISPLAY[slug],
                "cover": new_names[0],
                "images": new_names,
                "count": len(new_names),
            }
        )
        print(f"OK {slug}: kept {len(new_names)}")

    order_index = {s: i for i, s in enumerate(ORDER)}
    events_meta.sort(key=lambda e: order_index.get(e["slug"], 99))
    (EVENTS_IMG / "manifest.json").write_text(
        json.dumps(events_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return events_meta


def regenerate(events: list[dict]) -> None:
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
    lead = (
        "Voici les événements qui ont rassemblé la Compagnie. "
        "Les galeries ne montrent que des rôdeurs masqués, loin des traces du monde moderne."
    )
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
  <link rel="stylesheet/less" type="text/css" href="less/site.less">
  <link rel="stylesheet/less" type="text/css" href="less/page-inner.less">
  <link rel="stylesheet/less" type="text/css" href="less/evenements.less">
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
      <p>{lead}</p>
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

    EVENTS_HTML.mkdir(exist_ok=True)
    for old in EVENTS_HTML.glob("*.html"):
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
  <link rel="stylesheet/less" type="text/css" href="../less/site.less">
  <link rel="stylesheet/less" type="text/css" href="../less/page-inner.less">
  <link rel="stylesheet/less" type="text/css" href="../less/galerie.less">
  <link rel="stylesheet/less" type="text/css" href="../less/evenements.less">
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
        (EVENTS_HTML / f"{e['slug']}.html").write_text(page, encoding="utf-8")
        print(f"page {e['slug']}.html")


def update_sitemap(events: list[dict]) -> None:
    import re

    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    event_urls = ['  <url>\n    <loc>https://galadhrim-dagnir.com/evenements.html</loc>\n  </url>']
    for e in events:
        event_urls.append(
            f"  <url>\n    <loc>https://galadhrim-dagnir.com/evenements/{e['slug']}.html</loc>\n  </url>"
        )
    block = "\n".join(event_urls)
    pattern = re.compile(
        r"  <url>\n    <loc>https://galadhrim-dagnir.com/evenements\.html</loc>\n  </url>"
        r"(?:\n  <url>\n    <loc>https://galadhrim-dagnir.com/evenements/[^<]+</loc>\n  </url>)*",
        re.MULTILINE,
    )
    text = pattern.sub(block, text, count=1)
    sitemap.write_text(text, encoding="utf-8")
    print("Updated sitemap.xml")


def main() -> None:
    events = filter_and_renumber()
    regenerate(events)
    update_sitemap(events)
    total = sum(e["count"] for e in events)
    print(f"\n{len(events)} events, {total} photos kept")


if __name__ == "__main__":
    main()
