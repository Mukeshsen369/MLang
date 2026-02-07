from domains.base import Domain, DomainResponse
from domains.math import MathDomain
import re


class MathReasoningDomain(Domain):
    name = "MATH_REASONING"

    def __init__(self):
        self.math = MathDomain()

    def can_handle(self, context):
        text = context["raw_input"].lower()
        return any(t in text for t in [
            "a number", "sum of", "increased by",
            "decreased by", "minus", "equals",
            "becomes", "travels", "percent of"
        ])

    def handle(self, context):
        text = context["raw_input"].lower().strip()

        # -------- LINEAR WORD PROBLEMS --------
        equation = self._parse_linear_equation(text)
        if equation:
            context["raw_input"] = f"solve {equation}"
            result = self.math.handle(context)

            context["last_decision"] = {
                "type": "math_reasoning",
                "reason": (
                    "I converted the word problem into an equation.\n"
                    f"The equation was {equation}.\n"
                    "Then I solved it to find the unknown value."
                )
            }
            return result

        # -------- RATE PROBLEMS --------
        rate = self._parse_rate_problem(text)
        if rate:
            d, t, unit = rate
            speed = d / t

            context["last_decision"] = {
                "type": "math_reasoning",
                "reason": (
                    "Speed is calculated as distance divided by time.\n"
                    f"I divided {d} by {t}."
                )
            }
            return DomainResponse(True, f"The speed is {speed} {unit}.")

        # -------- PERCENTAGE --------
        percent = self._parse_percentage(text)
        if percent:
            p, v = percent
            result = (p / 100) * v

            context["last_decision"] = {
                "type": "math_reasoning",
                "reason": (
                    "Percent means per hundred.\n"
                    f"I calculated {p}% of {v}."
                )
            }
            return DomainResponse(True, f"{p} percent of {v} is {result}.")

        return DomainResponse(True, needs_clarification=True)

    # ---------------- HELPERS ----------------
    def _parse_linear_equation(self, text):
        if " and " in text or " or " in text:
            return None

        patterns = [
            (r"a number increased by (\d+) becomes (\d+)", "x + {} = {}"),
            (r"the sum of a number and (\d+) is (\d+)", "x + {} = {}"),
            (r"a number decreased by (\d+) becomes (\d+)", "x - {} = {}"),
            (r"a number minus (\d+) equals (\d+)", "x - {} = {}"),
        ]

        for pat, fmt in patterns:
            m = re.search(pat, text)
            if m:
                return fmt.format(*m.groups())
        return None

    def _parse_rate_problem(self, text):
        m = re.search(r"travels (\d+\.?\d*) .* in (\d+\.?\d*) hour", text)
        return (float(m[1]), float(m[2]), "km/h") if m else None

    def _parse_percentage(self, text):
        m = re.search(r"(\d+\.?\d*) percent of (\d+\.?\d*)", text)
        return (float(m[1]), float(m[2])) if m else None
