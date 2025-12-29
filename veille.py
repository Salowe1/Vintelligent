import os
import json
import time
import requests
import feedparser
from bs4 import BeautifulSoup
from google import genai

# Configuration Gemini
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_official_brvm_data():
    """Extraction robuste des cours BRVM"""
    url = "https://www.brvm.org/fr/cours-actions/0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On cherche toutes les lignes du tableau
        rows = soup.find_all('tr')
        stock_data = None
        
        # On cherche spécifiquement SONATEL ou la première ligne valide
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 5 and ("SONATEL" in cols[1].text.upper() or stock_data is None):
                # On nettoie les données (on enlève les espaces invisibles)
                stock_data = {
                    "titre": cols[1].text.strip(),
                    "prix": cols[3].text.strip().replace('\xa0', '') + " FCFA",
                    "variation": cols[8].text.strip(),
                    "maj": time.strftime("%d/%m/%Y %H:%M")
                }
                if "SONATEL" in cols[1].text.upper(): break

        if not stock_data: raise Exception("Tableau non trouvé")

    except Exception as e:
        print(f"Erreur Scraping: {e}")
        return {"titre": "SONATEL SN", "prix": "19 500 FCFA", "variation": "+0.5%", "maj": time.strftime("%d/%m/%Y"), "conseil": "Données en cours de rafraîchissement."}

    # Intelligence Artificielle Gemini 2.0
    try:
        prompt = f"Le titre {stock_data['titre']} affiche {stock_data['variation']}. Donne un conseil boursier pro de 10 mots max pour un investisseur UEMOA."
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        stock_data["conseil"] = response.text.strip().replace('*', '')
    except:
        stock_data["conseil"] = "Maintenir les positions sur les valeurs de rendement."
    
    return stock_data

def collect_intelligence():
    print("Mise à jour de l'intelligence financière...")
    data = {"bourse": get_official_brvm_data(), "articles": []}
    
    # News
    feed = feedparser.parse("https://www.financialafrik.com/feed/")
    for entry in feed.entries[:6]:
        data["articles"].append({
            "titre": entry.title,
            "lien": entry.link,
            "source": "Financial Afrik",
            "date": time.strftime("%d/%m/%Y")
        })

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collect_intelligence()
