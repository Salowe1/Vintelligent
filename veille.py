import os
import json
import time
import requests
import feedparser
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURATION GEMINI ---
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_official_brvm_data():
    """Extraction directe des données officielles BRVM"""
    url = "https://www.sikafinance.com/marches/cotations"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status() 
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    # Extraction de la première ligne de cotation (Top Gainer)
    top_row = table.find_all('tr')[1] 
    cols = top_row.find_all('td')
    
    stock_data = {
        "titre": cols[0].text.strip(),
        "prix": cols[1].text.strip() + " FCFA",
        "variation": cols[2].text.strip(),
        "maj": time.strftime("%d/%m/%Y %H:%M")
    }
    
    # Analyse IA en temps réel
    try:
        prompt = f"Analyse cette performance boursière UEMOA : {stock_data['titre']} à {stock_data['variation']}. Donne un conseil stratégique de 2 phrases maximum."
        ai_response = model.generate_content(prompt)
        stock_data["conseil"] = ai_response.text.strip().replace('"', '')
    except:
        stock_data["conseil"] = "Titre en forte progression. Analyse technique recommandée pour confirmer le point d'entrée."
    
    return stock_data

def collect_intelligence():
    print("Démarrage de la collecte officielle...")
    
    # 1. Bourse
    bourse = get_official_brvm_data()
    
    # 2. Flux RSS (Financial Afrik)
    news_feed = feedparser.parse("https://www.financialafrik.com/feed/")
    articles = []
    for entry in news_feed.entries[:6]:
        articles.append({
            "titre": entry.title,
            "resume": entry.summary[:180] + "..." if hasattr(entry, 'summary') else "",
            "lien": entry.link,
            "source": "Financial Afrik",
            "date": time.strftime("%d/%m/%Y")
        })

    # 3. Export JSON
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"articles": articles, "bourse": bourse}, f, ensure_ascii=False, indent=4)
    print("data.json mis à jour avec succès.")

if __name__ == "__main__":
    collect_intelligence()
