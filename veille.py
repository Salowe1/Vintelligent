import feedparser
import json
import time
import os
from haystack import Pipeline
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
from haystack.components.builders import PromptBuilder

# 1. Configuration de Gemini (Utilise la clé API stockée dans GitHub Secrets)
api_key = os.environ.get("GOOGLE_API_KEY")
gemini_generator = GoogleAIGeminiGenerator(model="gemini-2.0-flash", api_key=api_key)

prompt_template = """
Analyse cet article pour un expert en intelligence économique. 
Fournis un résumé stratégique de 2 phrases maximum en Français. 
Focus sur l'impact financier, géopolitique ou les opportunités d'investissement.
Article: {{content}}
Résumé:
"""
prompt_builder = PromptBuilder(template=prompt_template)

pipeline = Pipeline()
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("gemini", gemini_generator)
pipeline.connect("prompt_builder", "gemini")

# 2. Sources stratégiques (Focus Afrique et Business)
SOURCES = {
    "Agence Ecofin": "https://www.agenceecofin.com/newsletter/rss",
    "AllAfrica Business": "https://allafrica.com/tools/headlines/rdf/business/main.rdf",
    "Jeune Afrique": "https://www.jeuneafrique.com/feed/",
    "Africanews": "https://www.africanews.com/feed/rss",
    "AfDB News": "https://www.afdb.org/en/rss-feeds/news-and-events",
    "France24 Afrique": "https://www.france24.com/en/africa/rss"
}

def collecter():
    flux_complet = []
    
    for nom, url in SOURCES.items():
        print(f"Extraction : {nom}")
        feed = feedparser.parse(url)
        
        # On prend les 4 derniers articles par source
        for entry in feed.entries[:4]:
            try:
                # Préparation du contenu pour l'IA
                content = entry.get("summary", entry.title)
                
                print(f"Analyse IA : {entry.title[:50]}...")
                result = pipeline.run({"prompt_builder": {"content": content}})
                resume_ia = result["gemini"]["replies"][0]
                
                # Formatage de la date pour le HTML (ex: "24 Dec 2025")
                date_brute = entry.get("published", "Récent")
                date_propre = " ".join(date_brute.split(" ")[:4]) if " " in date_brute else date_brute
                
                flux_complet.append({
                    "source": nom,
                    "titre": entry.title,
                    "lien": entry.link,
                    "resume": resume_ia,
                    "date": date_propre
                })
                
                # Pause pour respecter les limites de l'API gratuite (15 RPM)
                time.sleep(4.5) 
                
            except Exception as e:
                print(f"Erreur sur un article : {e}")
                continue
    
    # Sauvegarde au format JSON
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(flux_complet, f, ensure_ascii=False, indent=4)
    print("Mise à jour de data.json terminée.")

if __name__ == "__main__":
    collecter()
