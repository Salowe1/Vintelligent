import os
import json
import time
import feedparser
from google import genai

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def collect_intelligence():
    # 1. Load data from R with fallback
    brvm_data = {"titre": "BRVM Marché", "prix": "---", "variation": "0.00%", "status": "error"}
    
    if os.path.exists("temp_brvm.json"):
        try:
            with open("temp_brvm.json", "r", encoding="utf-8") as f:
                temp = json.load(f)
                if temp.get("status") == "success":
                    brvm_data = temp
        except Exception as e:
            print(f"Error reading R output: {e}")

    # 2. AI Analysis
    try:
        if brvm_data["status"] == "success":
            prompt = f"Analyse {brvm_data['titre']} ({brvm_data['variation']}). Donne un conseil d'expert boursier en 10 mots maximum."
        else:
            prompt = "Donne un conseil général sur l'investissement en zone UEMOA en 10 mots."
            
        ai_msg = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        conseil = ai_msg.text.strip()
    except:
        conseil = "Analyse technique recommandée pour confirmer la tendance."

    # 3. Finalize Bourse Data
    bourse_final = {
        "titre": brvm_data.get("titre"),
        "prix": brvm_data.get("prix"),
        "variation": brvm_data.get("variation"),
        "conseil": conseil,
        "maj": time.strftime("%d/%m/%Y %H:%M")
    }

    # 4. News Feed
    articles = []
    try:
        feed = feedparser.parse("https://www.financialafrik.com/feed/")
        for entry in feed.entries[:6]:
            articles.append({
                "titre": entry.title,
                "lien": entry.link,
                "source": "Financial Afrik",
                "date": time.strftime("%d/%m/%Y"),
                "resume": (entry.summary[:150] + "...") if 'summary' in entry else "Analyse financière disponible."
            })
    except:
        articles = [{"titre": "Flux indisponible", "source": "Système", "date": "--", "resume": "Erreur de connexion RSS"}]

    # 5. Output
    final_output = {"bourse": bourse_final, "articles": articles}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collect_intelligence()
