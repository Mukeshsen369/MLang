from abc import ABC, abstractmethod


class ExternalProvider(ABC):
    """
    A provider returns factual summaries only.
    No reasoning. No memory. No assumptions.
    """

    name = "BASE"

    @abstractmethod
    def fetch(self, concept: str):
        """
        Returns:
        {
            "summaries": list[str],
            "confidence": float,
            "sources": list[str],
            "notes": str
        }
        or None if unavailable
        """
        pass
