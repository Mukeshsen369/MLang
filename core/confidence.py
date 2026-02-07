from enum import Enum, auto


class ConfidenceLevel(Enum):
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()
    CRITICAL = auto()


class ConfidenceResult:
    def __init__(self, level, reason=None):
        self.level = level
        self.reason = reason


class ConfidenceEvaluator:
    @staticmethod
    def evaluate(context):
        if context.get("risk_level") == "HIGH":
            return ConfidenceResult(ConfidenceLevel.CRITICAL, "High risk detected")

        if not context.get("intent"):
            return ConfidenceResult(ConfidenceLevel.LOW, "Intent unclear")

        return ConfidenceResult(ConfidenceLevel.HIGH)
