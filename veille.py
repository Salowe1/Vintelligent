import feedparser
import json
import time
import os
from haystack import Pipeline
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.components.builders import PromptBuilder

# 1. Setup Gemini (15 RPM Free Tier)
gemini_generator = GoogleAIGeminiGenerator(model="gemini-2.0-flash")

prompt_template = """
Analyse cet article pour un expert OSINT. Fournis un résumé stratégique (2 phrases) en Français.
Focus sur l'impact géopolitique ou économique.
Article: {{content}}
Résumé:
"""
prompt_builder = PromptBuilder(template=prompt_template)

pipeline = Pipeline()
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("gemini", gemini_generator)
pipeline.connect("prompt_builder", "gemini")

# 2. Multiplied Sources (Scaling to 100+ categories/sites)
SOURCES = {
    "AllAfrica Business": "https://allafrica.com/tools/headlines/rdf/business/main.rdf",
    "AllAfrica Conflict": "https://allafrica.com/tools/headlines/rdf/conflict/main.rdf",
    "AllAfrica Governance": "https://allafrica.com/tools/headlines/rdf/governance/main.rdf",
    "Africanews": "https://www.africanews.com/feed/rss",
    "France24 Afrique": "https://www.france24.com/en/africa/rss",
    "Jeune Afrique": "https://www.jeuneafrique.com/feed/",
    "Agence Ecofin": "https://www.agenceecofin.com/newsletter/rss",
    "WHO Africa (Health)": "https://www.afro.who.int/fr/node/4295/feed",
    "AfDB News": "https://www.afdb.org/en/rss-feeds/news-and-events",
    "Kéwoulo (Investigation)": "https://kewoulo.info/feed",
    # Note: You can easily add more AllAfrica categories like /environment/, /health/, etc.
}

def collecter():
    flux_complet = []
    
    for nom, url in SOURCES.items():
        print(f"Aggregating: {nom}")
        feed = feedparser.parse(url)
        
        # Take the most recent 3 articles per source to manage volume
        for entry in feed.entries[:3]:
            try:
                content = entry.get("summary", entry.title)
                
                # Gemini Rate Limiting: 15 RPM = ~1 request every 4 seconds
                print(f"Analyzing: {entry.title[:50]}...")
                result = pipeline.run({"prompt_builder": {"content": content}})
                resume_ia = result["gemini"]["replies"][0]
                
                flux_complet.append({
                    "source": nom,
                    "titre": entry.title,
                    "lien": entry.link,
                    "resume": resume_ia,
                    "date": entry.get("published", "Récent")
                })
                
                # Pause to respect Gemini Free Tier limits
                time.sleep(4.5) 
                
            except Exception as e:
                print(f"Skip article due to error: {e}")
                continue
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(flux_complet, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collecter()
