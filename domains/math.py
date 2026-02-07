from domains.base import Domain, DomainResponse
import re
import math


class MathDomain(Domain):
    name = "MATH"

    def can_handle(self, context):
        text = context["raw_input"].lower()
        return text.startswith("solve") or "=" in text

    def handle(self, context):
        text = context["raw_input"].lower().strip()
        context.pop("last_decision", None)

        if not text.startswith("solve"):
            return DomainResponse(False)

        equation = text.replace("solve", "", 1).strip()
        lhs, rhs = equation.split("=")
        lhs, rhs = lhs.strip(), rhs.strip()

        var = self._detect_variable(lhs + rhs)
        if not var:
            return DomainResponse(True, needs_clarification=True)

        try:
            sols, steps = self._solve(lhs, rhs, var)
        except Exception:
            return DomainResponse(True, needs_clarification=True)

        context["last_decision"] = {
            "type": "math",
            "reason": "\n".join(steps)
        }

        if not sols:
            return DomainResponse(True, "This equation has no real solution.")

        if len(sols) == 1:
            return DomainResponse(True, f"The solution is {var} = {sols[0]}.")

        sol_text = " and ".join(f"{var} = {s}" for s in sols)
        return DomainResponse(True, f"The solutions are {sol_text}.")

    # ---------------- SOLVER ----------------
    def _solve(self, lhs, rhs, var):
        expr = f"({lhs}) - ({rhs})".replace("^", "**")
        expr = re.sub(rf"(\d)({var})", r"\1*\2", expr)

        f = lambda x: eval(expr.replace(var, f"({x})"), {"__builtins__": {}})
        b = f(0)
        a = f(1) - b

        if abs(a) < 1e-12:
            return [], ["No unique solution exists."]

        sol = -b / a
        return [sol], [
            "I rearranged the equation into ax + b = 0.",
            f"I identified a = {a}, b = {b}.",
            f"I solved x = -b / a = {sol}."
        ]

    def _detect_variable(self, text):
        for ch in text:
            if ch.isalpha():
                return ch
        return None
