from domains.base import Domain, DomainResponse
import sympy as sp


class AdvancedMathDomain(Domain):
    name = "ADVANCED_MATH"

    def can_handle(self, context):
        return "limit" in context["raw_input"].lower()

    def handle(self, context):
        x = sp.symbols("x")
        text = context["raw_input"].lower()

        try:
            expr = sp.sympify(text.split("limit")[1].split("as")[0])
            point = float(text.split("->")[1])
            result = sp.limit(expr, x, point)

            context["last_decision"] = {
                "type": "advanced_math",
                "reason": (
                    "I evaluated the limit using standard limit rules\n"
                    "and symbolic simplification."
                )
            }
            return DomainResponse(True, f"The limit is {result}.")
        except Exception:
            return DomainResponse(True, needs_clarification=True)
