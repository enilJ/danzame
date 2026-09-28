"""Genera il sito danzame.it a partire dai contenuti.

Legge:
  contenuti/coreografie/*.yml   una scheda per coreografia
  contenuti/festival.yml        il Mò.DANCEFEST in evidenza
  contenuti/home/{it,en,fr}.yml i testi della home
  img/                          le foto (anche originali grandi: vengono ridotte qui)

Scrive il sito pronto in _site/ (italiano alla radice, inglese in en/, francese in fr/).

Uso:  python strumenti/genera.py
"""
import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lingue import COMMON, LANG_NAMES, LANGS, MONTHS_IT, WORKS_UI, tr_work  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
MODELLI = ROOT / "strumenti" / "modelli"
SITE = "https://danzame.it/"
LUOGHI = ("Svizzera", "Sicilia", "Altrove")
MAX_LATO = 1400          # lato lungo massimo delle foto pubblicate
MAX_LATO_APERTURA = 1800
MAX_IN_HOME = 6

errori = []


def carica(path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        errori.append(f"{path.relative_to(ROOT)}: il file non è scritto correttamente ({e})")
        return {}


def L(v, lang):
    """Testo nella lingua richiesta: accetta sia una stringa sia {it:…, en:…, fr:…}."""
    if isinstance(v, dict):
        return v.get(lang) or v.get("it") or ""
    return "" if v is None else str(v)


# ---------------------------------------------------------------------------
# Foto
# ---------------------------------------------------------------------------
dimensioni = {}


def prepara_immagini():
    for src in sorted((ROOT / "img").rglob("*")):
        if not src.is_file() or src.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        rel = src.relative_to(ROOT).as_posix()
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        lato = MAX_LATO_APERTURA if "img/home/" in rel else MAX_LATO
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            if src.suffix.lower() == ".png" or max(im.size) <= lato and src.stat().st_size < 900_000:
                shutil.copy2(src, dst)
                dimensioni[rel] = im.size
                continue
            im = im.convert("RGB")
            im.thumbnail((lato, lato))
            im.save(dst, "JPEG", quality=80, optimize=True, progressive=True)
            dimensioni[rel] = im.size


# ---------------------------------------------------------------------------
# Coreografie
# ---------------------------------------------------------------------------
def carica_coreografie():
    works = []
    for p in sorted((ROOT / "contenuti" / "coreografie").glob("*.yml")):
        if p.name.startswith("_"):
            continue
        d = carica(p)
        if not d:
            continue
        slug = p.stem
        if not d.get("titolo") or not isinstance(d.get("anno"), int):
            errori.append(f"{p.name}: servono almeno 'titolo' e 'anno' (un numero, es. 2026)")
            continue
        luogo = d.get("luogo", "Altrove")
        if luogo not in LUOGHI:
            errori.append(f"{p.name}: 'luogo' deve essere Svizzera, Sicilia o Altrove (trovato: {luogo})")
            luogo = "Altrove"
        foto = []
        for f in d.get("foto") or []:
            f = {"file": f} if isinstance(f, str) else f
            rel = f"img/coreografie/{f.get('file', '')}"
            if not (ROOT / rel).exists():
                errori.append(f"{p.name}: la foto {f.get('file')} non è nella cartella img/coreografie/")
                continue
            foto.append({"src": rel, "credito": f.get("credito", "")})
        works.append({
            "slug": slug, "titolo": str(d["titolo"]), "anno": d["anno"], "place": luogo,
            "anteprima": str(d.get("anteprima", "") or ""), "prima": str(d.get("prima", "") or ""),
            "organico": str(d.get("organico", "") or ""), "compagnia": str(d.get("compagnia", "") or ""),
            "musica": str(d.get("musica", "") or ""),
            "repliche": [str(x) for x in d.get("repliche") or []], "prossimamente": [],
            "citazioni": d.get("citazioni") or [], "note": [str(x) for x in d.get("note") or []],
            "foto": foto, "in_home": bool(d.get("in_home")), "luogo_breve": d.get("luogo_breve", ""),
        })
    return works


def data_riga(s):
    """Ultima data leggibile in una riga (giorno mese anno, in italiano)."""
    anni = list(re.finditer(r"\b(19|20)\d{2}\b", s))
    if not anni:
        return None
    y = anni[-1]
    prima = s[: y.start()].lower()
    pos, mese = max(((prima.rfind(m), i + 1) for i, m in enumerate(MONTHS_IT)), default=(-1, 0))
    if pos < 0:
        return datetime.date(int(y.group(0)), 12, 31)
    giorni = re.findall(r"(\d{1,2})", prima[:pos])
    g = int(giorni[-1]) if giorni else 1
    try:
        return datetime.date(int(y.group(0)), mese, g)
    except ValueError:
        return datetime.date(int(y.group(0)), mese, 1)


def dividi_date(w, oggi):
    passate, future = [], []
    for e in w["repliche"]:
        d = data_riga(e)
        (future if d and d >= oggi else passate).append(e)
    return dict(w, repliche=passate, prossimamente=future)


# ---------------------------------------------------------------------------
# Pagine
# ---------------------------------------------------------------------------
def prefisso(lang):
    return "" if lang == "it" else "../"


def cartella(lang):
    return "" if lang == "it" else lang + "/"


def selettore_lingua(cur, page):
    r = prefisso(cur)
    links = []
    for l in LANGS:
        attuale = ' aria-current="true"' if l == cur else ""
        links.append(f'<a href="{r}{cartella(l)}{page}" hreflang="{l}" lang="{l}" title="{LANG_NAMES[l]}"{attuale}>{l}</a>')
    return f'<span class="langs" role="group" aria-label="{COMMON[cur]["lang_label"]}">' + "".join(links) + "</span>"


def hreflang(page):
    p = "" if page == "index.html" else page
    tags = [f'<link rel="alternate" hreflang="{l}" href="{SITE}{cartella(l)}{p}">' for l in LANGS]
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{p}">')
    return "\n".join(tags)


MANTIENI_SCHEDA = """<script>document.querySelectorAll('.langs a').forEach(a=>a.addEventListener('click',()=>{a.href=a.href.split('#')[0]+location.hash}));</script>"""


def riempi(tpl, values):
    def rep(m):
        k = m.group(1)
        if k not in values:
            raise KeyError(f"testo mancante: {k}")
        return str(values[k])
    return re.sub(r"\[\[(\w+)\]\]", rep, tpl)


def documento(lang, corpo, descrizione):
    head, _, rest = corpo.partition("<header")
    return (f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="description" content="{html.escape(descrizione)}">\n'
            f'<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>\n'
            f'{head}</head>\n<body>\n<header{rest}\n</body>\n</html>\n')


def ordinale(n, lang):
    if lang == "it":
        return f"{n}ª edizione"
    if lang == "fr":
        return f"{n}{'re' if n == 1 else 'e'} édition"
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf} edition"


def festival_html(fest, lang, t, r):
    giorni = []
    for g in fest.get("giorni") or []:
        artisti = "".join(
            f'<li>{html.escape(L(a.get("nome"), lang))}{" <span>· " + html.escape(L(a.get("da"), lang)) + "</span>" if a.get("da") else ""}</li>'
            for a in g.get("artisti") or [])
        giorni.append(
            f'<div class="day"><span class="d">{g.get("giorno", "")}<small>{html.escape(L(g.get("nome"), lang))}</small></span><div>'
            f'<h4>{html.escape(L(g.get("titolo"), lang))}</h4><p>{html.escape(L(g.get("testo"), lang))}</p>'
            + (f"<ul>{artisti}</ul>" if artisti else "") + "</div></div>")
    days = f'<div class="days">{"".join(giorni)}</div>' if giorni else ""
    partners = (f'<p class="partners"><b>{t["partners"]}</b> {html.escape(L(fest.get("partner"), lang))} {t["patronage"]}</p>'
                if fest.get("partner") else "")
    foto = fest.get("foto") or []
    if foto:
        figs = []
        for f in foto:
            f = {"file": f} if isinstance(f, str) else f
            rel = f"img/festival/{f['file']}"
            if not (ROOT / rel).exists():
                errori.append(f"festival.yml: la foto {f['file']} non è nella cartella img/festival/")
                continue
            figs.append(f'<figure><img loading="lazy" src="{r}{rel}" alt="Mò.DANCEFEST {fest.get("anno", "")}"></figure>')
        crediti = sorted({f.get("credito") for f in foto if isinstance(f, dict) and f.get("credito")})
        photos = f'<div class="fest-gallery">{"".join(figs)}</div>' + (
            f'<p class="label photo-credit">{WORKS_UI[lang]["photo"]}: {html.escape(", ".join(crediti))}</p>' if crediti else "")
    else:
        photos = f'<div class="photo-slot"><p>{t["slot_title"].replace("{anno}", str(fest.get("anno", "")))}</p><span class="label">{t["slot_note"]}</span></div>'
    past = "".join(
        f'<figure><div class="th"><img loading="lazy" src="{r}img/festival/{e["locandina"]}" alt="{t["poster_word"]} {e["anno"]}"></div>'
        f'<figcaption><span>{e["anno"]}</span><span class="muted">{html.escape(L(e.get("didascalia"), lang))}</span></figcaption></figure>'
        for e in fest.get("edizioni_precedenti") or [])
    return days, partners, photos, past


def pagina_home(lang, works, fest):
    t = carica(ROOT / "contenuti" / "home" / f"{lang}.yml")
    t_it = carica(ROOT / "contenuti" / "home" / "it.yml")
    if errori:
        print("Da correggere prima di pubblicare:")
        for e in errori:
            print("  -", e)
        sys.exit(1)
    t = {**t_it, **t}
    c = COMMON[lang]
    r = prefisso(lang)
    n = str(len(works))
    in_home = sorted([w for w in works if w["in_home"]], key=lambda w: -w["anno"])[:MAX_IN_HOME]
    cards = []
    for w in in_home:
        dove = w["luogo_breve"] or WORKS_UI[lang]["places"][w["place"]]
        img = (f'<div class="ph"><img loading="lazy" src="{r}{w["foto"][0]["src"]}" alt="{html.escape(w["titolo"])}"></div>'
               if w["foto"] else f'<div class="ph nophoto"><span class="label">{t["photo_soon"]}</span></div>')
        cards.append(f'<a class="card" href="coreografie.html#{w["slug"]}">{img}<span class="t">{html.escape(w["titolo"])}</span>'
                     f'<span class="m">{w["anno"]} · {html.escape(str(dove))}</span></a>')
    seasons = "\n".join(
        f'<div class="season{" here" if str(s["anno"]) == "2010" else ""}"><span class="when">{s["anno"]}</span>'
        f'<div class="where">{s["luogo"]}<span>{s["teatro"]}</span></div><p>{s["testo"]}</p></div>'
        for s in t["seasons"])
    righe = lambda rows: "".join(f'<li><span class="y">{x["anno"]}</span><span>{x["testo"]}</span></li>' for x in rows)
    days, partners, photos, past = festival_html(fest, lang, t, r)
    values = {**c, **{k: str(v).replace("[[n_works]]", n) for k, v in t.items() if not isinstance(v, (list, dict))},
              "r": r, "css": (MODELLI / "home.css").read_text(encoding="utf-8"),
              "hreflang": hreflang("index.html"), "langswitch": selettore_lingua(lang, "index.html"),
              "cards": "\n        ".join(cards), "seasons": seasons,
              "awards": righe(t["awards"]), "juries": righe(t["juries"]),
              "fest_edition": ordinale(fest.get("edizione", ""), lang), "fest_dates": L(fest.get("date"), lang),
              "fest_poster": fest.get("locandina", ""), "fest_days": days, "fest_partners": partners,
              "fest_photos": photos, "fest_past": past}
    corpo = riempi((MODELLI / "home.html").read_text(encoding="utf-8"), values) + MANTIENI_SCHEDA
    descr = re.sub("<[^>]+>", "", t["intro_lede"])
    return corpo, documento(lang, corpo, descr)


def pagina_coreografie(lang, works):
    ui = WORKS_UI[lang]
    c = COMMON[lang]
    r = prefisso(lang)
    oggi = datetime.date.today()
    data, photos = [], {}
    for w in works:
        d = tr_work(dividi_date(w, oggi), lang)
        data.append({k: d[k] for k in ("slug", "titolo", "anno", "place", "anteprima", "prima", "organico", "compagnia",
                                       "musica", "repliche", "prossimamente", "citazioni", "note")}
                    | {"crediti": sorted({f["credito"] for f in w["foto"] if f["credito"]})})
        if w["foto"]:
            photos[w["slug"]] = [{"src": r + f["src"], "w": dimensioni.get(f["src"], (0, 0))[0],
                                  "h": dimensioni.get(f["src"], (0, 0))[1]} for f in w["foto"]]
    T = {**ui, "choreo_by": c["choreo_by"]}
    values = {**c, **{k: v for k, v in ui.items() if isinstance(v, str)}, "lang": lang,
              "hreflang": hreflang("coreografie.html"), "langswitch": selettore_lingua(lang, "coreografie.html"),
              "pl_sv": ui["places"]["Svizzera"], "pl_si": ui["places"]["Sicilia"], "pl_al": ui["places"]["Altrove"]}
    out = riempi((MODELLI / "coreografie.html").read_text(encoding="utf-8"), values)
    out = (out.replace("/*DATA*/", json.dumps(data, ensure_ascii=False))
              .replace("/*PHOTOS*/", json.dumps(photos, ensure_ascii=False))
              .replace("/*T*/", json.dumps(T, ensure_ascii=False)))
    return out.replace("</body>", MANTIENI_SCHEDA + "\n</body>")


def pagina_404():
    """Pagina per gli indirizzi inesistenti: rimanda i vecchi link di WordPress alle pagine nuove."""
    vecchi = carica(ROOT / "contenuti" / "vecchi-indirizzi.yml")
    mappa = {str(k).rstrip("/") + "/": str(v or "") for k, v in vecchi.items()}
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>danz@m.e</title>
<script>
(function(){{
  var mappa = {json.dumps(mappa, ensure_ascii=False)};
  var p = location.pathname, base = "/";
  var m = p.match(/^\/[^\/]+\//);
  if (m && location.hostname.endsWith("github.io")) {{ base = m[0]; p = "/" + p.slice(base.length); }}
  if (!p.endsWith("/")) p += "/";
  if (p in mappa) location.replace(base + mappa[p]);
}})();
</script>
<style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#F2F3F6;color:#12141A;font-family:Georgia,serif;padding:24px;text-align:center}}
h1{{font-weight:400;font-size:40px;margin:0 0 12px}} p{{font-family:system-ui,sans-serif;color:#5A6072}} a{{color:#2436D2}}
@media (prefers-color-scheme:dark){{body{{background:#0D0F15;color:#ECEEF3}} p{{color:#959CAE}} a{{color:#8492FF}}}}
</style>
</head>
<body>
<div><h1>Pagina non trovata</h1><p>Page not found · Page introuvable</p><p><a id="home" href="/">danz@m.e</a></p></div>
<script>if(location.hostname.endsWith("github.io")){{var b=location.pathname.match(/^\/[^\/]+\//);if(b)document.getElementById("home").href=b[0];}}</script>
</body>
</html>
"""


def main():
    anteprima = "--anteprima" in sys.argv
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    prepara_immagini()
    works = carica_coreografie()
    fest = carica(ROOT / "contenuti" / "festival.yml")
    if errori:
        print("Da correggere prima di pubblicare:")
        for e in errori:
            print("  -", e)
        sys.exit(1)
    pagine = []
    for lang in LANGS:
        d = OUT / cartella(lang)
        d.mkdir(exist_ok=True)
        corpo, doc = pagina_home(lang, works, fest)
        (d / "index.html").write_text(corpo if anteprima and lang == "it" else doc, encoding="utf-8")
        (d / "coreografie.html").write_text(pagina_coreografie(lang, works), encoding="utf-8")
        pagine += [f"{SITE}{cartella(lang)}", f"{SITE}{cartella(lang)}coreografie.html"]
    if errori:
        print("Da correggere prima di pubblicare:")
        for e in errori:
            print("  -", e)
        sys.exit(1)
    oggi = datetime.date.today().isoformat()
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{oggi}</lastmod></url>\n" for u in pagine) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "404.html").write_text(pagina_404(), encoding="utf-8")
    print(f"Sito generato in _site/: {len(works)} coreografie, {len(dimensioni)} immagini, 3 lingue.")


if __name__ == "__main__":
    main()
