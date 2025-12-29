import os
import json
import time
import requests
import feedparser
from bs4 import BeautifulSoup
# Correct import for the NEW SDK (post-2025 standard)
from google import genai
from google.genai import types

# The client picks up GOOGLE_API_KEY automatically from environment variables
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_official_brvm_data():
    """Fetches real data from the official BRVM exchange and selects the best performer"""
    url = "https://www.brvm.org/fr/cours-actions/0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', {'class': 'views-table'})
        rows = table.find('tbody').find_all('tr')
        
        # Logic to find the best daily performer (highest variation %)
        best_stock = None
        max_var = -99.0

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 8:
                try:
                    var_str = cols[8].text.strip().replace('%', '').replace(',', '.')
                    current_var = float(var_str)
                    if current_var > max_var:
                        max_var = current_var
                        best_stock = {
                            "titre": cols[1].text.strip(),
                            "prix": cols[3].text.strip() + " FCFA",
                            "variation": cols[8].text.strip(),
                            "maj": time.strftime("%d/%m/%Y %H:%M")
                        }
                except ValueError:
                    continue

        if not best_stock:
            raise Exception("No data parsed")
            
        stock_data = best_stock

    except Exception as e:
        print(f"Scraping error: {e}")
        return {"titre": "BRVM Composite", "prix": "--", "variation": "0%", "maj": "Sync...", "conseil": "Analyse indisponible."}

    # AI Intelligence using the 2.0 Flash model
    try:
        prompt = f"Analyse {stock_data['titre']} avec une hausse de {stock_data['variation']}. Donne un conseil d'investissement pro en 10 mots maximum."
        ai_msg = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        stock_data["conseil"] = ai_msg.text.strip()
    except:
        stock_data["conseil"] = "Forte tendance haussière détectée. Surveiller les volumes d'achat."
    
    return stock_data

def collect_intelligence():
    print("Connecting to official UEMOA sources...")
    data = {
        "bourse": get_official_brvm_data(),
        "articles": []
    }
    
    # News feed
    feed = feedparser.parse("https://www.financialafrik.com/feed/")
    for entry in feed.entries[:6]:
        # Generate a brief summary for the UI
        resume = entry.summary[:150] + "..." if hasattr(entry, 'summary') else "Consultez l'article pour plus d'informations sur l'économie africaine."
        data["articles"].append({
            "titre": entry.title,
            "lien": entry.link,
            "source": "Financial Afrik",
            "date": time.strftime("%d/%m/%Y"),
            "resume": resume
        })

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Intelligence update successful.")

if __name__ == "__main__":
    collect_intelligence()
