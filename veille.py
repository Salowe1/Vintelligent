import feedparser
import json
from datetime import datetime

# Configuration des sources
SOURCES = {
    "Jeune Afrique": "https://www.jeuneafrique.com/feed/",
    "Agence Ecofin": "https://www.agenceecofin.com/newsletter/rss",
    "African Business": "https://african.business/feed/",
    "La Tribune Afrique": "https://afrique.latribune.fr/rss.xml"
}

def collecter():
    flux_complet = []
    for nom, url in SOURCES.items():
        print(f"Extraction : {nom}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            flux_complet.append({
                "source": nom,
                "titre": entry.title,
                "lien": entry.link,
                "resume": entry.get("summary", "")[:250] + "...",
                "date": entry.get("published", "Date inconnue")
            })
    
    # On sauvegarde les données en JSON pour le site web
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(flux_complet, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collecter()
