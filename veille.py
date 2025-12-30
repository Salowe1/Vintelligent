import os
import json
import time
import feedparser
from google import genai

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def collect_intelligence():
    # Load R results or use fallback
    if os.path.exists("temp_brvm.json"):
        with open("temp_brvm.json", "r", encoding="utf-8") as f:
            brvm_data = json.load(f)
    else:
        brvm_data = {"status": "error", "titre": "Marché BRVM", "variation": "0%", "prix": "---"}

    # Gemini Analysis
    try:
        if brvm_data.get("status") == "success":
            prompt = f"Explique pourquoi l'action {brvm_data['titre']} a varié de {brvm_data['variation']} et donne un conseil pro en 10 mots."
        else:
            prompt = "Donne une brève tendance actuelle sur la bourse BRVM WAEMU en 10 mots."
            
        ai_msg = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        conseil = ai_msg.text.strip()
    except:
        conseil = "Analyse des flux financiers en cours. Prudence recommandée."

    # Final JSON structure
    final_output = {
        "bourse": {
            "titre": brvm_data.get("titre", "BRVM"),
            "prix": brvm_data.get("prix", "---"),
            "variation": brvm_data.get("variation", "0%"),
            "conseil": conseil,
            "maj": time.strftime("%d/%m/%Y %H:%M")
        },
        "articles": []
    }

    # RSS Feed Parsing
    try:
        feed = feedparser.parse("https://www.financialafrik.com/feed/")
        for entry in feed.entries[:6]:
            final_output["articles"].append({
                "titre": entry.title,
                "lien": entry.link,
                "source": "Financial Afrik",
                "date": time.strftime("%d/%m/%Y"),
                "resume": entry.summary[:150] + "..." if 'summary' in entry else "Cliquez pour lire l'article."
            })
    except:
        pass

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collect_intelligence()
