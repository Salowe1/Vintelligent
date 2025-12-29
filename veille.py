import os
import json
import time
import requests
import feedparser
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURATION ---
# Ensure GOOGLE_API_KEY is set in GitHub Secrets
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_official_brvm_data():
    """Fetches official live market data from the UEMOA zone"""
    url = "https://www.sikafinance.com/marches/cotations"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status() # Crashes script if site is down (No simulation)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    # Row 1 is usually the top gainer of the day
    top_row = table.find_all('tr')[1] 
    cols = top_row.find_all('td')
    
    stock_data = {
        "titre": cols[0].text.strip(),
        "prix": cols[1].text.strip() + " FCFA",
        "variation": cols[2].text.strip(),
        "maj": time.strftime("%d/%m/%Y %H:%M")
    }
    
    # AI Analysis of the official data
    prompt = f"Analyse cette performance boursière BRVM: {stock_data['titre']} à {stock_data['variation']}. Donne un conseil pro de 2 phrases pour un investisseur en Afrique de l'Ouest."
    ai_response = model.generate_content(prompt)
    stock_data["conseil"] = ai_response.text.strip()
    
    return stock_data

def collect_intelligence():
    print("Connecting to official UEMOA financial sources...")
    
    # 1. Official Market Data
    bourse = get_official_brvm_data()
    
    # 2. Official News Feed
    news_feed = feedparser.parse("https://www.financialafrik.com/feed/")
    if not news_feed.entries:
        raise Exception("Failed to fetch official news feed")
        
    articles = []
    for entry in news_feed.entries[:6]:
        articles.append({
            "titre": entry.title,
            "resume": entry.summary[:200] + "..." if hasattr(entry, 'summary') else "",
            "lien": entry.link,
            "source": "Financial Afrik",
            "date": time.strftime("%d/%m/%Y")
        })

    # 3. Final Data Assembly
    final_output = {
        "articles": articles,
        "bourse": bourse,
        "status": "OFFICIAL_DATA_LIVE"
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
    print("Intelligence update complete.")

if __name__ == "__main__":
    collect_intelligence()
