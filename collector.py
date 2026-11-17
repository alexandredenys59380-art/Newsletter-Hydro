import re
import html
import feedparser
from urllib.parse import quote
from datetime import datetime, timezone
from database import init_db, save_article

# Sources RSS publiques. Ajouter ou retirer des flux dans cette liste.
RSS_SOURCES = [
    ("EDF - communiqués de presse", "https://www.edf.fr/tous-les-communiques/feed"),
    ("France Hydro Électricité", "https://www.france-hydro-electricite.fr/feed/"),
    ("Connaissance des Énergies", "https://www.connaissancedesenergies.org/rss.xml"),
    ("Google News - EDF Hydro", "https://news.google.com/rss/search?q=" + quote('"EDF Hydro" OR "hydroélectricité EDF"') + "&hl=fr&gl=FR&ceid=FR:fr"),
    ("Google News - barrages et hydroélectricité", "https://news.google.com/rss/search?q=" + quote('(EDF OR "EDF Hydro") (barrage OR turbine OR centrale hydroélectrique OR hydroélectricité)') + "&hl=fr&gl=FR&ceid=FR:fr"),
]

KEYWORDS = [
    "edf hydro", "hydroélectricité", "hydro-électricité", "barrage",
    "centrale hydroélectrique", "turbine", "turbines", "turbine hydraulique",
    "pompage-turbinage", "step", "durance", "verdon", "rhone", "rhône",
    "alpes", "hydraulique", "groupe de production", "concession hydroélectrique"
]

def clean_text(value):
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()

def classify(text):
    t = text.lower()
    if any(k in t for k in ["biodivers", "poisson", "environnement", "écologique", "faune", "flore"]):
        return "Environnement & biodiversité"
    if any(k in t for k in ["maintenance", "rénovation", "chantier", "travaux", "modernisation", "réfection"]):
        return "Maintenance & travaux"
    if any(k in t for k in ["investissement", "investit", "construction", "projet", "millions d'euros", "m€"]):
        return "Projets & investissements"
    if any(k in t for k in ["production", "exploitation", "crue", "débit", "étiage", "gestion de l'eau"]):
        return "Production & exploitation"
    if any(k in t for k in ["réglementation", "concession", "décret", "arrêté", "tarif", "marché de l'électricité"]):
        return "Réglementation & marché"
    if any(k in t for k in ["recrut", "emploi", "alternance", "salarié", "formation", "direction"]):
        return "Entreprise & ressources humaines"
    return "Autres"

def is_relevant(title, summary, source):
    text = f"{title} {summary} {source}".lower()
    return any(keyword in text for keyword in KEYWORDS)

def parse_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
    return None

def collect_all():
    init_db()
    inserted = 0
    for source_name, feed_url in RSS_SOURCES:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = clean_text(entry.get("title", "Publication sans titre"))
                summary = clean_text(entry.get("summary", entry.get("description", "")))
                url = entry.get("link", "").strip()
                if not url or not is_relevant(title, summary, source_name):
                    continue
                article = {
                    "url": url,
                    "title": title,
                    "source": source_name,
                    "published": parse_date(entry),
                    "summary": summary,
                    "category": classify(f"{title} {summary}")
                }
                if save_article(article):
                    inserted += 1
        except Exception as exc:
            print(f"[ERREUR] {source_name}: {exc}")
    print(f"Collecte terminée : {inserted} nouvelle(s) publication(s).")
    return inserted

if __name__ == "__main__":
    collect_all()
