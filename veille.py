import feedparser
import json
import os
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret

# 1. Setup Haystack Intelligence Pipeline
prompt_template = """
Analyze this news for an OSINT expert. Provide a concise, strategic summary (2 sentences max) in French.
Focus on regional impact.
Article: {{content}}
Summary:
"""
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"), model="gpt-4o-mini")

pipeline = Pipeline()
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("llm", llm)
pipeline.connect("prompt_builder", "llm")

SOURCES = {
    "Jeune Afrique": "https://www.jeuneafrique.com/feed/",
    "Agence Ecofin": "https://www.agenceecofin.com/newsletter/rss",
    "African Business": "https://african.business/feed/",
    "La Tribune Afrique": "https://afrique.latribune.fr/rss.xml"
}

def collecter():
    flux_complet = []
    for nom, url in SOURCES.items():
        print(f"Processing: {nom}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # Top 3 per source for speed
            # Use Haystack to summarize
            content = entry.get("summary", entry.title)
            result = pipeline.run({"prompt_builder": {"content": content}})
            resume_ia = result["llm"]["replies"][0]

            flux_complet.append({
                "source": nom,
                "titre": entry.title,
                "lien": entry.link,
                "resume": resume_ia,
                "date": entry.get("published", "Récemment")
            })
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(flux_complet, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    collecter()
