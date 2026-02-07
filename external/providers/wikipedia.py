import wikipedia
from external.providers.base import ExternalProvider


class WikipediaProvider(ExternalProvider):
    name = "Wikipedia"

    def fetch(self, concept: str):
        try:
            summary = wikipedia.summary(concept, sentences=2, auto_suggest=False)
            return {
                "summaries": [summary],
                "confidence": 0.6,
                "sources": ["Wikipedia"],
                "notes": "Community-edited source."
            }
        except Exception:
            return None
