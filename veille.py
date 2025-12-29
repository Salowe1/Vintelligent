import os
import json
import time
import requests
import feedparser
from google import genai

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def collect_intelligence():
    # 1. Load the data prepared by R
    try:
        with open("temp_brvm.json", "r", encoding="utf-8") as f:
            brvm_raw = json.load(f)
    except:
        brvm_raw = {"titre": "BRVM Index", "prix": "--", "variation": "0%"}

    # 2. AI Analysis via Gemini 2.0 Flash
    try:
        prompt = f"Analyse {brvm_raw['titre']} ({brvm_raw['variation']}). Donne un conseil d'expert boursier en 10 mots."
        ai_msg = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        conseil = ai_msg.text.strip()
    except:
        conseil = "Analyse technique recommandée pour confirmer la tendance."

    # 3. Finalize Bourse Data
    bourse_final = {
        **brvm_raw,
        "conseil": conseil,
        "maj": time.strftime("%d/%m/%Y %H:%M")
    }

    # 4. News Feed
    articles = []
    feed = feedparser.parse("https://www.financialafrik.com/feed/")
    for entry in feed.entries[:6]:
        articles.append({
            "titre": entry.title,
            "lien": entry.link,
            "source": "Financial Afrik",
            "date": time.strftime("%d/%m/%Y"),
            "resume": entry.summary[:150] + "..." if 'summary' in entry else "Analyse financière disponible."
        })

    # 5. Output for Website
    final_output = {"bourse": bourse_final, "articles": articles}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collect_intelligence()
