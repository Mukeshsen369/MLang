from external.providers.wikipedia import WikipediaProvider
from external.confidence import aggregate
from dataclasses import dataclass


@dataclass
class ExternalKnowledgeRequest:
    concept: str
    strict: bool = False


@dataclass
class ExternalKnowledgeResult:
    concept: str
    summaries: list
    confidence: float
    sources: list
    notes: str = ""


class ExternalKnowledgeInterface:
    def __init__(self):
        self.providers = [
            WikipediaProvider(),
        ]

    def fetch(self, request: ExternalKnowledgeRequest):
        collected = []

        for provider in self.providers:
            result = provider.fetch(request.concept)
            if result:
                collected.append(result)

        if not collected:
            return ExternalKnowledgeResult(
                request.concept, [], 0.0, [],
                "No reliable external sources found."
            )

        confidence = aggregate(collected)

        if request.strict and confidence < 0.4:
            return ExternalKnowledgeResult(
                request.concept, [], confidence, [],
                "Confidence too low under strict mode."
            )

        summaries = []
        sources = []
        notes = []

        for r in collected:
            summaries.extend(r["summaries"])
            sources.extend(r["sources"])
            if r.get("notes"):
                notes.append(r["notes"])

        return ExternalKnowledgeResult(
            concept=request.concept,
            summaries=summaries,
            confidence=confidence,
            sources=list(set(sources)),
            notes=" | ".join(set(notes))
        )
