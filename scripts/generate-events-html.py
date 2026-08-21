from pathlib import Path
import json
import html

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "images" / "evenements" / "manifest.json"
EVENTS_DIR = ROOT / "evenements"

NAV_FR = """  <nav>
    <a href="{prefix}index.html">Accueil</a>
    <a href="{prefix}presentation.html">Présentation</a>
    <a href="{prefix}evenements.html">Événements</a>
    <a href="{prefix}activites.html">Activités</a>
    <a href="{prefix}rejoindre.html">Rejoindre</a>
    <a href="{prefix}contact.html">Contact</a>
    <a href="{prefix}legendes.html">Histoire & Légendes</a>
  </nav>"""

FOOTER = """  <footer>
    <p>© Galadhrim Dagnir – 9ème Compagnie de Rôdeurs du Gondor</p>
  </footer>"""

LIGHTBOX = """  <div id="gd-lightbox" class="gd-lightbox" role="dialog" aria-modal="true" aria-label="Agrandissement de la photo">
    <div class="gd-lightbox-backdrop" aria-hidden="true"></div>
    <button type="button" class="gd-lightbox-close" aria-label="Fermer">×</button>
    <button type="button" class="gd-lightbox-prev" aria-label="Image précédente">‹</button>
    <button type="button" class="gd-lightbox-next" aria-label="Image suivante">›</button>
    <figure class="gd-lightbox-inner">
      <img src="" alt="">
      <figcaption></figcaption>
    </figure>
  </div>"""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def listing_page(events: list) -> str:
    cards = []
    for e in events:
        cover_name = Path(e["cover"]).with_suffix(".webp").name
        cover = f"images/evenements/{e['slug']}/{cover_name}"
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

    og_image = f"https://galadhrim-dagnir.com/images/evenements/{events[0]['slug']}/{events[0]['cover']}"

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Événements – Galadhrim Dagnir</title>
  <meta name="description" content="Événements de la 9ème Compagnie de Rôdeurs Galadhrim Dagnir : camps, festivals et rencontres — photos et souvenirs." />
  <link rel="canonical" href="https://galadhrim-dagnir.com/evenements.html" />
  <meta property="og:title" content="Événements – Galadhrim Dagnir" />
  <meta property="og:description" content="Camps, festivals et rencontres des Rôdeurs du Gondor." />
  <meta property="og:image" content="{og_image}" />
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
{NAV_FR.format(prefix="")}

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

{FOOTER}
</body>
</html>
"""


def event_page(e: dict) -> str:
    imgs = []
    for name in e["images"]:
        src = f"../images/evenements/{e['slug']}/{name}"
        alt = esc(e["name"])
        imgs.append(f'      <a href="{esc(src)}"><img src="{esc(src)}" alt="{alt}" loading="lazy"></a>')

    cover = f"https://galadhrim-dagnir.com/images/evenements/{e['slug']}/{e['cover']}"
    count_label = "1 photo" if e["count"] == 1 else f"{e['count']} photos"

    return f"""<!DOCTYPE html>
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
{NAV_FR.format(prefix="../")}

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

{LIGHTBOX}

{FOOTER}

  <script src="../js/gallery-lightbox.js"></script>
</body>
</html>
"""


def redirect_galerie() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=evenements.html">
  <link rel="canonical" href="https://galadhrim-dagnir.com/evenements.html" />
  <title>Redirection – Événements</title>
  <script>location.replace("evenements.html");</script>
</head>
<body>
  <p><a href="evenements.html">Voir les événements</a></p>
</body>
</html>
"""


def main() -> None:
    events = json.loads(MANIFEST.read_text(encoding="utf-8"))
    (ROOT / "evenements.html").write_text(listing_page(events), encoding="utf-8")
    print("Wrote evenements.html")

    EVENTS_DIR.mkdir(exist_ok=True)
    for e in events:
        path = EVENTS_DIR / f"{e['slug']}.html"
        path.write_text(event_page(e), encoding="utf-8")
        print("Wrote", path.name)

    (ROOT / "galerie.html").write_text(redirect_galerie(), encoding="utf-8")
    print("Wrote galerie.html redirect")


if __name__ == "__main__":
    main()
