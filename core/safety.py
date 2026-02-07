from enum import Enum, auto


class RiskLevel(Enum):
    NONE = auto()
    HIGH = auto()


class SafetyResult:
    def __init__(self, level, reason=None):
        self.level = level
        self.reason = reason


class SafetyEvaluator:
    DESTRUCTIVE = {"delete", "remove", "erase", "destroy"}

    @staticmethod
    def evaluate(text):
        for w in SafetyEvaluator.DESTRUCTIVE:
            if w in text.lower():
                return SafetyResult(RiskLevel.HIGH, "Destructive action")
        return SafetyResult(RiskLevel.NONE)
