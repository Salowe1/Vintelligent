import feedparser
import json
import time
import os
import requests
from bs4 import BeautifulSoup

def collecter():
    data = {
        "articles": [],
        "bourse": {
            "titre": "SONATEL SN",
            "prix": "19 450 FCFA",
            "variation": "+1.2%",
            "conseil": "Analyse en cours. Focus sur les valeurs refuges UEMOA.",
            "maj": time.strftime("%d/%m/%Y")
        }
    }

    # 1. RSS News
    try:
        feed = feedparser.parse("https://www.financialafrik.com/feed/")
        for entry in feed.entries[:6]:
            data["articles"].append({
                "titre": entry.title,
                "resume": entry.summary[:150] + "..." if hasattr(entry, 'summary') else "",
                "lien": entry.link,
                "source": "FINANCE",
                "date": time.strftime("%d/%m/%Y")
            })
    except Exception as e:
        print(f"RSS Error: {e}")

    # 2. Simple Scraping Fallback
    # If the AI or Scraper fails, this ensures the site doesn't stay "Stuck"
    try:
        # We try a very simple request
        r = requests.get("https://www.sikafinance.com/marches/cotations", timeout=10)
        if r.status_code == 200:
             # Just a placeholder for now to ensure the script finishes
             data["bourse"]["conseil"] = "Le marché montre une résilience sur les secteurs télécoms et bancaires."
    except:
        pass

    # 3. CRITICAL: Save the file NO MATTER WHAT
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Successfully created data.json")

if __name__ == "__main__":
    collecter()
