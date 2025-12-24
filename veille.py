import feedparser
import json
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator # Or HuggingFaceLocalGenerator
from haystack.utils import Secret

# 1. Define the Haystack Summary Pipeline
prompt_template = """
Synthesize the following news article into a one-sentence strategic insight for an OSINT analyst.
Focus on the impact for the African region.
Article: {{content}}
Insight:
"""

prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"), model="gpt-4o-mini")

pipeline = Pipeline()
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("llm", llm)
pipeline.connect("prompt_builder", "llm")

def collecter():
    flux_complet = []
    for nom, url in SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]: # Processing top 5 for speed
            content = entry.get("summary", "")
            
            # Run Haystack Pipeline
            result = pipeline.run({"prompt_builder": {"content": content}})
            insight = result["llm"]["replies"][0]

            flux_complet.append({
                "source": nom,
                "titre": entry.title,
                "resume": insight, # Now it's an AI-generated summary!
                "lien": entry.link,
                "date": entry.get("published", "")
            })
    # ... save to data.json
