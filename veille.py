import os
import json
import time
import requests
import feedparser
from bs4 import BeautifulSoup
# The canonical way to import the new SDK
from google import genai 
from google.genai import types

# --- CONFIGURATION GEMINI ---
# The client automatically looks for GOOGLE_API_KEY in environment variables
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_official_brvm_data():
    """Fetches official live market data from BRVM.org"""
    url = "https://www.brvm.org/fr/cours-actions/0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status() 
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the table row with the most active or first stock
    # Note: BRVM table structure uses specific classes
    try:
        table = soup.find('table', {'class': 'views-table'})
        top_row = table.find('tbody').find('tr')
        cols = top_row.find_all('td')
        
        stock_data = {
            "titre": cols[1].text.strip(), # Name
            "prix": cols[3].text.strip() + " FCFA", # Last price
            "variation": cols[8].text.strip(), # Change %
            "maj": time.strftime("%d/%m/%Y %H:%M")
        }
    except Exception as e:
        print(f"Extraction error: {e}")
        # Return a 'Service Unavailable' dict rather than crashing everything
        return {
            "titre": "Marché BRVM",
            "prix": "--",
            "variation": "0.0%",
            "conseil": "Données en cours de synchronisation avec la place boursière.",
            "maj": time.strftime("%d/%m/%Y")
        }
    
    # AI Analysis with the new SDK
    try:
        prompt = f"Analyse cette performance boursière : {stock_data['titre']} à {stock_data['variation']}. Donne un conseil très court (15 mots max) pour un investisseur."
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        stock_data["conseil"] = response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        stock_data["conseil"] = "Analyse indisponible pour le moment."
    
    return stock_data

def collect_intelligence():
    print("Démarrage de la collecte officielle...")
    
    # 1. Bourse
    bourse = get_official_brvm_data()
    
    # 2. News
    news_feed = feedparser.parse("https://www.financialafrik.com/feed/")
    articles = []
    for entry in news_feed.entries[:6]:
        articles.append({
            "titre": entry.title,
            "resume": entry.summary[:150] + "..." if hasattr(entry, 'summary') else "",
            "lien": entry.link,
            "source": "Financial Afrik",
            "date": time.strftime("%d/%m/%Y")
        })

    # 3. Export
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"articles": articles, "bourse": bourse}, f, ensure_ascii=False, indent=4)
    print("Mise à jour terminée.")

if __name__ == "__main__":
    collect_intelligence()
