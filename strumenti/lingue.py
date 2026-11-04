"""Testi fissi dell'interfaccia in italiano, inglese, francese e tedesco, e traduzione
automatica di date e formule ricorrenti nelle schede delle coreografie.

L'italiano è la lingua di partenza. Le traduzioni vanno fatte rileggere
(idealmente da Enrico, il tedesco da qualcuno di madrelingua) prima di andare online.
"""
import re

LANGS = ["it", "en", "fr", "de"]
LANG_NAMES = {"it": "Italiano", "en": "English", "fr": "Français", "de": "Deutsch"}

# ---------------------------------------------------------------------------
# Interfaccia comune (menu, piè di pagina)
# ---------------------------------------------------------------------------
COMMON = {
    "it": {
        "nav_works": "Coreografie", "nav_fest": "Mò.DANCEFEST", "nav_bio": "Biografia", "nav_contact": "Contatti",
        "nav_label": "Principale", "lang_label": "Lingua",
        "motto": "Danza come arte in movimento, senza trucchi.",
        "footer_assoc": "Associazione Culturale DANZ@M.E · Acireale",
        "footer_legal": "C.F. e P.IVA 04082100878", "nav_privacy": "Privacy",
        "choreo_by": "Coreografia",
    },
    "en": {
        "nav_works": "Works", "nav_fest": "Mò.DANCEFEST", "nav_bio": "Biography", "nav_contact": "Contact",
        "nav_label": "Main", "lang_label": "Language",
        "motto": "Dance as art in motion, without tricks.",
        "footer_assoc": "DANZ@M.E Cultural Association · Acireale",
        "footer_legal": "Tax code and VAT no. 04082100878", "nav_privacy": "Privacy",
        "choreo_by": "Choreography",
    },
    "fr": {
        "nav_works": "Chorégraphies", "nav_fest": "Mò.DANCEFEST", "nav_bio": "Biographie", "nav_contact": "Contact",
        "nav_label": "Principal", "lang_label": "Langue",
        "motto": "La danse comme art en mouvement, sans trucs.",
        "footer_assoc": "Association culturelle DANZ@M.E · Acireale",
        "footer_legal": "Code fiscal et n° de TVA 04082100878", "nav_privacy": "Confidentialité",
        "choreo_by": "Chorégraphie",
    },
    "de": {
        "nav_works": "Choreografien", "nav_fest": "Mò.DANCEFEST", "nav_bio": "Biografie", "nav_contact": "Kontakt",
        "nav_label": "Hauptmenü", "lang_label": "Sprache",
        "motto": "Tanz als Kunst in Bewegung, ohne Tricks.",
        "footer_assoc": "Kulturverein DANZ@M.E · Acireale",
        "footer_legal": "Steuernummer und USt-IdNr. 04082100878", "nav_privacy": "Datenschutz",
        "choreo_by": "Choreografie",
    },
}

# ---------------------------------------------------------------------------
# Pagina Coreografie
# ---------------------------------------------------------------------------
WORKS_UI = {
    "it": {
        "page_title": "Coreografie", "eyebrow": "Archivio", "h1": "Coreografie",
        "places": {"Svizzera": "Svizzera", "Sicilia": "Sicilia", "Altrove": "Altrove"},
        "in_place": {"Svizzera": "in Svizzera", "Sicilia": "in Sicilia", "Altrove": "altrove"},
        "works_word": "lavori",
        "legend_note": "Numero di prime per anno. Tocca una barra per andare a quell'anno.",
        "premiere_one": "prima", "premiere_many": "prime",
        "return_note": "2010 · rientro in Sicilia",
        "f_period": "Periodo", "f_place": "Luogo", "all": "Tutti", "everywhere": "Ovunque",
        "search": "Cerca", "search_ph": "Cerca titolo, compagnia, musica…",
        "empty": "Nessun lavoro corrisponde alla ricerca.",
        "back": "← Tutte le coreografie",
        "k_preview": "Anteprima", "k_premiere": "Prima", "k_cast": "Organico", "k_for": "Per",
        "k_company": "Compagnia", "k_music": "Musica",
        "press": "Dalla stampa", "reruns": "Repliche", "upcoming": "Prossime date", "notes": "Note",
        "photo": "Foto", "enlarge": "Ingrandisci foto {k} di {n}", "photo_alt": "{t}, foto {k}",
        "close": "Chiudi", "pager": "Scorri l'archivio",
        "decades": [
            {"id": "2020", "a": "Anni", "b": "2020", "chip": "2020",
             "note": "Le creazioni per MoDem PRO e CZD2 a Catania, e i progetti con gli ensemble giovanili svizzeri."},
            {"id": "2010", "a": "Anni", "b": "2010", "chip": "2010",
             "note": "Il ritorno in Sicilia e l'inizio del ciclo Muddica a Scenario Pubblico."},
            {"id": "2000", "a": "Anni", "b": "2000", "chip": "2000",
             "note": "Tra la Svizzera e la Sicilia: DANZ@M.E, i duetti con Daniela Campione, la Cinevox Dance Company."},
            {"id": "1990", "a": "Anni", "b": "'90", "chip": "'90",
             "note": "Le prime coreografie all'Opernhaus di Zurigo e allo Stadttheater di Lucerna, poi la ORMA Dance Company."},
        ],
    },
    "en": {
        "page_title": "Works", "eyebrow": "Archive", "h1": "Works",
        "places": {"Svizzera": "Switzerland", "Sicilia": "Sicily", "Altrove": "Elsewhere"},
        "in_place": {"Svizzera": "in Switzerland", "Sicilia": "in Sicily", "Altrove": "elsewhere"},
        "works_word": "works",
        "legend_note": "Premieres per year. Tap a bar to jump to that year.",
        "premiere_one": "premiere", "premiere_many": "premieres",
        "return_note": "2010 · return to Sicily",
        "f_period": "Period", "f_place": "Place", "all": "All", "everywhere": "Everywhere",
        "search": "Search", "search_ph": "Search title, company, music…",
        "empty": "No works match your search.",
        "back": "← All works",
        "k_preview": "Preview", "k_premiere": "Premiere", "k_cast": "Cast", "k_for": "For",
        "k_company": "Company", "k_music": "Music",
        "press": "Press", "reruns": "Further performances", "upcoming": "Upcoming dates", "notes": "Notes",
        "photo": "Photos", "enlarge": "Enlarge photo {k} of {n}", "photo_alt": "{t}, photo {k}",
        "close": "Close", "pager": "Browse the archive",
        "decades": [
            {"id": "2020", "a": "The", "b": "2020s", "chip": "2020s",
             "note": "Creations for MoDem PRO and CZD2 in Catania, and projects with Swiss youth ensembles."},
            {"id": "2010", "a": "The", "b": "2010s", "chip": "2010s",
             "note": "The return to Sicily and the start of the Muddica cycle at Scenario Pubblico."},
            {"id": "2000", "a": "The", "b": "2000s", "chip": "2000s",
             "note": "Between Switzerland and Sicily: DANZ@M.E, the duets with Daniela Campione, the Cinevox Dance Company."},
            {"id": "1990", "a": "The", "b": "1990s", "chip": "1990s",
             "note": "First choreographies at the Zurich Opera House and the Lucerne Stadttheater, then the ORMA Dance Company."},
        ],
    },
    "fr": {
        "page_title": "Chorégraphies", "eyebrow": "Archives", "h1": "Chorégraphies",
        "places": {"Svizzera": "Suisse", "Sicilia": "Sicile", "Altrove": "Ailleurs"},
        "in_place": {"Svizzera": "en Suisse", "Sicilia": "en Sicile", "Altrove": "ailleurs"},
        "works_word": "créations",
        "legend_note": "Nombre de premières par année. Touchez une barre pour aller à cette année.",
        "premiere_one": "première", "premiere_many": "premières",
        "return_note": "2010 · retour en Sicile",
        "f_period": "Période", "f_place": "Lieu", "all": "Toutes", "everywhere": "Partout",
        "search": "Rechercher", "search_ph": "Titre, compagnie, musique…",
        "empty": "Aucune création ne correspond à la recherche.",
        "back": "← Toutes les chorégraphies",
        "k_preview": "Avant-première", "k_premiere": "Première", "k_cast": "Distribution", "k_for": "Pour",
        "k_company": "Compagnie", "k_music": "Musique",
        "press": "Presse", "reruns": "Reprises", "upcoming": "Prochaines dates", "notes": "Notes",
        "photo": "Photos", "enlarge": "Agrandir la photo {k} sur {n}", "photo_alt": "{t}, photo {k}",
        "close": "Fermer", "pager": "Parcourir les archives",
        "decades": [
            {"id": "2020", "a": "Années", "b": "2020", "chip": "2020",
             "note": "Les créations pour MoDem PRO et CZD2 à Catane, et les projets avec les ensembles de jeunes en Suisse."},
            {"id": "2010", "a": "Années", "b": "2010", "chip": "2010",
             "note": "Le retour en Sicile et le début du cycle Muddica à Scenario Pubblico."},
            {"id": "2000", "a": "Années", "b": "2000", "chip": "2000",
             "note": "Entre la Suisse et la Sicile : DANZ@M.E, les duos avec Daniela Campione, la Cinevox Dance Company."},
            {"id": "1990", "a": "Années", "b": "90", "chip": "90",
             "note": "Les premières chorégraphies à l'Opernhaus de Zurich et au Stadttheater de Lucerne, puis l'ORMA Dance Company."},
        ],
    },
    "de": {
        "page_title": "Choreografien", "eyebrow": "Archiv", "h1": "Choreografien",
        "places": {"Svizzera": "Schweiz", "Sicilia": "Sizilien", "Altrove": "Anderswo"},
        "in_place": {"Svizzera": "in der Schweiz", "Sicilia": "in Sizilien", "Altrove": "anderswo"},
        "works_word": "Arbeiten",
        "legend_note": "Uraufführungen pro Jahr. Tippen Sie auf einen Balken, um zu diesem Jahr zu springen.",
        "premiere_one": "Uraufführung", "premiere_many": "Uraufführungen",
        "return_note": "2010 · Rückkehr nach Sizilien",
        "f_period": "Zeitraum", "f_place": "Ort", "all": "Alle", "everywhere": "Überall",
        "search": "Suchen", "search_ph": "Titel, Compagnie, Musik suchen…",
        "empty": "Keine Arbeit entspricht der Suche.",
        "back": "← Alle Choreografien",
        "k_preview": "Voraufführung", "k_premiere": "Uraufführung", "k_cast": "Besetzung", "k_for": "Für",
        "k_company": "Compagnie", "k_music": "Musik",
        "press": "Pressestimmen", "reruns": "Weitere Vorstellungen", "upcoming": "Nächste Termine", "notes": "Anmerkungen",
        "photo": "Fotos", "enlarge": "Foto {k} von {n} vergrößern", "photo_alt": "{t}, Foto {k}",
        "close": "Schließen", "pager": "Im Archiv blättern",
        "decades": [
            {"id": "2020", "a": "Die", "b": "2020er", "chip": "2020er",
             "note": "Kreationen für MoDem PRO und CZD2 in Catania und Projekte mit Schweizer Jugendensembles."},
            {"id": "2010", "a": "Die", "b": "2010er", "chip": "2010er",
             "note": "Die Rückkehr nach Sizilien und der Beginn des Muddica-Zyklus bei Scenario Pubblico."},
            {"id": "2000", "a": "Die", "b": "2000er", "chip": "2000er",
             "note": "Zwischen der Schweiz und Sizilien: DANZ@M.E, die Duette mit Daniela Campione, die Cinevox Dance Company."},
            {"id": "1990", "a": "Die", "b": "90er", "chip": "90er",
             "note": "Erste Choreografien am Opernhaus Zürich und am Stadttheater Luzern, dann die ORMA Dance Company."},
        ],
    },
}

# ---------------------------------------------------------------------------
# Traduzione dei campi delle schede (date e formule ricorrenti)
# ---------------------------------------------------------------------------
MONTHS_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
             "agosto", "settembre", "ottobre", "novembre", "dicembre"]
MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
           "August", "September", "Oktober", "November", "Dezember"],
}

# Formule ricorrenti; l'ordine conta (le più lunghe prima).
PHRASES = {
    "en": [
        ("Coreografo, regista e interprete, Assolo con Nello Toscano al violoncello",
         "Choreographer, director and performer; solo with Nello Toscano on cello"),
        ("Solo con Claudia Fichera performer", "Solo with performer Claudia Fichera"),
        ("partecipazione coreografica", "choreographic contribution"),
        ("Partecipazione coreografica", "Choreographic contribution"),
        ("danzatori con orchestra", "dancers with orchestra"),
        ("Duo con ", "Duo with "), ("danzatori", "dancers"),
        ("Giovani coreografi", "Young choreographers"),
        ("OPERNHAUS DI ZURIGO", "ZURICH OPERA HOUSE"),
        ("Tour Mauritius per Le Ballet de Lucerne", "Mauritius tour with Le Ballet de Lucerne"),
        ("Tour in Sicilia", "Sicily tour"), ("Tour Sicilia", "Sicily tour"),
        ("Tour Mauritius", "Mauritius tour"),
        ("Finalista al Prix Volinine, 1995 Parigi", "Finalist, Prix Volinine, Paris 1995"),
        ("Finalista Wettbewerb Internationalen", "Finalist, Internationaler Wettbewerb"),
        ("2° Premio Genzano di Roma", "2nd Prize, Genzano di Roma"),
        ("Versione rivisitata: 8 dancers", "Revised version: 8 dancers"),
        ("Per la Schweizer kammerballett, 1999:", "With the Schweizer Kammerballett, 1999:"),
        ("Filippine", "Philippines"),
        ("Theaterhaus Gessnerallee per Plate-Forme", "Theaterhaus Gessnerallee for the Plate-Forme"),
        ("per I DanzAteliers Youth Ensemble", "with I DanzAteliers Youth Ensemble"),
        ("Ospite Coreografo", "guest choreographer"), ("Guest Coreografo", "guest choreographer"),
        ("Zurigo", "Zurich"), ("Parigi", "Paris"),
        ("pianoforte:", "piano:"), (" e ", " and "),
        ("direttore d'orchestra", "conductor"), ("ensemble del conservatorio", "ensemble of the conservatory"),
    ],
    "fr": [
        ("Coreografo, regista e interprete, Assolo con Nello Toscano al violoncello",
         "Chorégraphe, metteur en scène et interprète ; solo avec Nello Toscano au violoncelle"),
        ("Solo con Claudia Fichera performer", "Solo avec la performeuse Claudia Fichera"),
        ("partecipazione coreografica", "participation chorégraphique"),
        ("Partecipazione coreografica", "Participation chorégraphique"),
        ("danzatori con orchestra", "danseurs avec orchestre"),
        ("Duo con ", "Duo avec "), ("danzatori", "danseurs"),
        ("Giovani coreografi", "Jeunes chorégraphes"),
        ("OPERNHAUS DI ZURIGO", "OPERNHAUS DE ZURICH"),
        ("Tour Mauritius per Le Ballet de Lucerne", "Tournée à l'île Maurice avec Le Ballet de Lucerne"),
        ("Tour in Sicilia", "Tournée en Sicile"), ("Tour Sicilia", "Tournée en Sicile"),
        ("Tour Mauritius", "Tournée à l'île Maurice"),
        ("Finalista al Prix Volinine, 1995 Parigi", "Finaliste du Prix Volinine, Paris 1995"),
        ("Finalista Wettbewerb Internationalen", "Finaliste, Internationaler Wettbewerb"),
        ("2° Premio Genzano di Roma", "2e Prix, Genzano di Roma"),
        ("Versione rivisitata: 8 danseurs", "Version revisitée : 8 danseurs"),
        ("Per la Schweizer kammerballett, 1999:", "Avec le Schweizer Kammerballett, 1999 :"),
        ("Filippine", "Philippines"),
        ("Theaterhaus Gessnerallee per Plate-Forme", "Theaterhaus Gessnerallee pour la Plate-Forme"),
        ("per I DanzAteliers Youth Ensemble", "avec I DanzAteliers Youth Ensemble"),
        ("Ospite Coreografo", "chorégraphe invité"), ("Guest Coreografo", "chorégraphe invité"),
        ("Zurigo", "Zurich"), ("Parigi", "Paris"),
        ("pianoforte:", "piano :"), (" e ", " et "),
        ("direttore d'orchestra", "direction"), ("ensemble del conservatorio", "ensemble du conservatoire"),
    ],
    "de": [
        ("Coreografo, regista e interprete, Assolo con Nello Toscano al violoncello",
         "Choreograf, Regisseur und Interpret; Solo mit Nello Toscano am Violoncello"),
        ("Solo con Claudia Fichera performer", "Solo mit der Performerin Claudia Fichera"),
        ("partecipazione coreografica", "choreografische Mitwirkung"),
        ("Partecipazione coreografica", "Choreografische Mitwirkung"),
        ("danzatori con orchestra", "Tänzerinnen und Tänzer mit Orchester"),
        ("Duo con ", "Duo mit "), ("danzatori", "Tänzerinnen und Tänzer"),
        ("Giovani coreografi", "Junge Choreografen"),
        ("OPERNHAUS DI ZURIGO", "OPERNHAUS ZÜRICH"),
        ("Tour Mauritius per Le Ballet de Lucerne", "Mauritius-Tournee mit Le Ballet de Lucerne"),
        ("Tour in Sicilia", "Sizilien-Tournee"), ("Tour Sicilia", "Sizilien-Tournee"),
        ("Tour Mauritius", "Mauritius-Tournee"),
        ("Finalista al Prix Volinine, 1995 Parigi", "Finalist beim Prix Volinine, Paris 1995"),
        ("Finalista Wettbewerb Internationalen", "Finalist, Internationaler Wettbewerb"),
        ("2° Premio Genzano di Roma", "2. Preis, Genzano di Roma"),
        ("Versione rivisitata: 8 Tänzerinnen und Tänzer", "Überarbeitete Fassung: 8 Tänzerinnen und Tänzer"),
        ("Per la Schweizer kammerballett, 1999:", "Mit dem Schweizer Kammerballett, 1999:"),
        ("Filippine", "Philippinen"),
        ("Theaterhaus Gessnerallee per Plate-Forme", "Theaterhaus Gessnerallee für die Plate-Forme"),
        ("per I DanzAteliers Youth Ensemble", "mit I DanzAteliers Youth Ensemble"),
        ("Ospite Coreografo", "Gastchoreograf"), ("Guest Coreografo", "Gastchoreograf"),
        ("Zurigo", "Zürich"), ("Zurich", "Zürich"), ("Parigi", "Paris"), ("Argovia", "Aargau"),
        ("pianoforte:", "Klavier:"), (" e ", " und "),
        ("direttore d'orchestra", "Dirigent"), ("ensemble del conservatorio", "Ensemble des Konservatoriums"),
    ],
}

# Mesi tedeschi, per aggiungere il punto ai giorni: "20 Juni" -> "20. Juni", "9 und 10 Januar" -> "9. und 10. Januar"
_MESI_DE = "|".join(MONTHS["de"])
_GIORNO_DE = re.compile(r"\b(\d{1,2})(?=(?:\s*(?:und|–|-|,|/)\s*\d{1,2})*\s+(?:%s)\b)" % _MESI_DE)

def tr_text(s, lang):
    if lang == "it" or not s:
        return s
    s = re.sub(r"\b1°\s", "1 ", s)
    for i, m in enumerate(MONTHS_IT):
        s = re.sub(r"\b%s\b" % m, MONTHS[lang][i], s, flags=re.I)
    for a, b in PHRASES[lang]:
        s = s.replace(a, b)
    if lang == "de":
        s = _GIORNO_DE.sub(r"\1.", s)
    return s


def tr_work(w, lang):
    w = dict(w)
    for k in ("prima", "anteprima", "organico", "compagnia"):
        w[k] = tr_text(w[k], lang)
    if lang != "it":
        w["musica"] = w["musica"].replace(" e ", {"en": " and ", "fr": " et ", "de": " und "}[lang])
    if w["musica"] in ("Live", "mix", "Collage", "collage", "varie"):
        w["musica"] = {"en": {"varie": "various"}, "fr": {"varie": "divers"},
                       "de": {"varie": "verschiedene"}}.get(lang, {}).get(w["musica"], w["musica"])
    for k in ("repliche", "prossimamente"):
        w[k] = [tr_text(x, lang) for x in w[k]]
    w["citazioni"] = [dict(c, traduzione=c.get("traduzione_" + lang, "") if lang != "it" else "") for c in w.get("citazioni", [])]
    return w
