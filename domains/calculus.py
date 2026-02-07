from domains.base import Domain, DomainResponse
import re


class CalculusDomain(Domain):
    name = "CALCULUS"

    # --------------------------------------------------
    def can_handle(self, context):
        text = context["raw_input"].lower()
        return any(t in text for t in [
            "integral of",
            "area under",
            "definite integral",
            "∫",
            "derivative",
            "rate of change",
        ])

    # --------------------------------------------------
    def handle(self, context):
        raw = context["raw_input"].strip()
        text = raw.lower().replace(" ", "")

        # ==================================================
        # SYMBOLIC INDEFINITE INTEGRAL: ∫ f(x) dx
        # ==================================================
        if text.startswith("∫") and text.endswith("dx"):
            func = text[1:-2]
            return self._indefinite_integral(func, context)

        # ==================================================
        # NATURAL LANGUAGE INDEFINITE INTEGRAL
        # ==================================================
        m = re.fullmatch(r"integralof(.+)", text)
        if m:
            func = m.group(1)
            return self._indefinite_integral(func, context)

        # ==================================================
        # DEFINITE INTEGRAL
        # ==================================================
        m = re.search(
            r"(areaunder|integralof|definiteintegralof)(.+)from(\d+\.?\d*)to(\d+\.?\d*)",
            text
        )
        if m:
            func = m.group(2)
            a = float(m.group(3))
            b = float(m.group(4))
            return self._definite_integral(func, a, b, context)

        return DomainResponse(True, needs_clarification=True)

    # ==================================================
    # INDEFINITE INTEGRAL CORE
    # ==================================================
    def _indefinite_integral(self, func, context):
        terms = self._parse_terms(func)
        if not terms:
            return DomainResponse(True, needs_clarification=True)

        results = []
        explanation = [
            "This is an indefinite integral.",
            "I applied the power rule and linearity of integration."
        ]

        for coeff, power in terms:
            antider = self._integrate_term(coeff, power)
            results.append(antider)
            explanation.append(
                f"The integral of {self._term_str(coeff, power)} is {antider}."
            )

        result_expr = " + ".join(results)

        context["last_decision"] = {
            "type": "calculus",
            "reason": "\n".join(explanation) + "\nAdding constant of integration C."
        }

        return DomainResponse(
            True,
            f"The integral is {result_expr} + C."
        )

    # ==================================================
    # DEFINITE INTEGRAL CORE
    # ==================================================
    def _definite_integral(self, func, a, b, context):
        terms = self._parse_terms(func)
        if not terms:
            return DomainResponse(True, needs_clarification=True)

        explanation = [
            "This is a definite integral.",
            "I first found the antiderivative."
        ]

        def F(x):
            total = 0
            for coeff, power in terms:
                total += coeff * (x ** (power + 1)) / (power + 1)
            return total

        upper = F(b)
        lower = F(a)
        area = upper - lower

        explanation.append(f"F({b}) = {upper}")
        explanation.append(f"F({a}) = {lower}")
        explanation.append(f"F({b}) − F({a}) = {area}")

        context["last_decision"] = {
            "type": "calculus",
            "reason": "\n".join(explanation)
        }

        return DomainResponse(
            True,
            f"The definite integral is {area}."
        )

    # ==================================================
    # TERM PARSER
    # ==================================================
    def _parse_terms(self, expr):
        expr = expr.strip()

        # remove brackets
        if expr.startswith("(") and expr.endswith(")"):
            expr = expr[1:-1]

        parts = re.split(r"\+", expr)
        terms = []

        for part in parts:
            m = re.fullmatch(r"(\d*)x(\^(\d+))?", part)
            if m:
                coeff = int(m.group(1)) if m.group(1) else 1
                power = int(m.group(3)) if m.group(3) else 1
                terms.append((coeff, power))
                continue

            if part.isdigit():
                terms.append((int(part), 0))
                continue

            return None  # unsupported term

        return terms

    # ==================================================
    # HELPERS
    # ==================================================
    def _integrate_term(self, coeff, power):
        new_power = power + 1
        return f"{coeff}/{new_power}*x^{new_power}"

    def _term_str(self, coeff, power):
        if power == 1:
            return f"{coeff}x"
        return f"{coeff}x^{power}"
