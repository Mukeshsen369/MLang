# ==========================================
# MLang - Entry Point (FINAL FIX)
# ==========================================

import copy

from core.engine import Engine
from core.confidence import ConfidenceEvaluator, ConfidenceLevel
from core.safety import SafetyEvaluator
from interface.cli import CLI

from memory.memory import Memory
from persistence.store import PersistenceStore

from domains.knowledge import KnowledgeDomain
from domains.math import MathDomain
from domains.math_reasoning import MathReasoningDomain
from domains.calculus import CalculusDomain
from domains.advanced_math import AdvancedMathDomain
from domains.data import DataDomain
from domains.why import WhyDomain


class MLangApplication:
    def __init__(self):
        self.engine = Engine()

        # ---------- Load persistent storage ----------
        saved = PersistenceStore.load()

        memory = Memory()
        memory.load(saved.get("user_knowledge"))
        self.engine.context["memory"] = memory

        self.engine.context["data_store"] = saved.get("data_store", {})
        self.engine.context["history"] = []
        self.engine.context["future"] = []

        # ---------- Register domains (ORDER MATTERS) ----------
        self.domains = [
            WhyDomain(),
            AdvancedMathDomain(),
            MathReasoningDomain(),
            CalculusDomain(),
            MathDomain(),
            KnowledgeDomain(),
            DataDomain(),
        ]

    # --------------------------------------------------
    # SNAPSHOT FOR UNDO / REDO
    # --------------------------------------------------
    def _snapshot(self, description):
        self.engine.context["history"].append({
            "data_store": copy.deepcopy(self.engine.context["data_store"]),
            "user_knowledge": copy.deepcopy(
                self.engine.context["memory"].export()
            ),
            "description": description
        })
        self.engine.context["future"].clear()

    # --------------------------------------------------
    # MAIN EXECUTION
    # --------------------------------------------------
    def execute(self):
        context = self.engine.context
        raw_input = context.get("raw_input", "")
        raw = raw_input.strip().lower()

        # ---------------- UNDO ----------------
        if raw.startswith("undo"):
            parts = raw.split()
            return self.engine.undo(int(parts[1])) if len(parts) == 2 and parts[1].isdigit() else self.engine.undo()

        # ---------------- REDO ----------------
        if raw.startswith("redo"):
            parts = raw.split()
            return self.engine.redo(int(parts[1])) if len(parts) == 2 and parts[1].isdigit() else self.engine.redo()

        # --------------------------------------------------
        # 🔥 DOMAIN ROUTING (FIRST — CRITICAL FIX)
        # --------------------------------------------------
        for domain in self.domains:
            if domain.can_handle(context):
                response = domain.handle(context)

                if response.needs_clarification:
                    return "I need a bit more clarity. Can you explain what you mean?"

                if response.handled:
                    self._persist()
                    return response.message

        # --------------------------------------------------
        # 🔹 DATA ASSIGNMENT (FALLBACK ONLY)
        # --------------------------------------------------
        if (
            "=" in raw
            and not raw.startswith(("solve", "evaluate", "calculate"))
            and not any(op in raw for op in ["==", ">=", "<="])
        ):
            name, values = raw.split("=", 1)
            name = name.strip()

            numbers = []
            for t in values.replace(",", " ").split():
                try:
                    numbers.append(float(t))
                except ValueError:
                    continue

            if numbers:
                self._snapshot(f"Stored '{name}'")
                context["data_store"][name] = numbers
                self._persist()
                return f"Stored {numbers} as '{name}'."

        # --------------------------------------------------
        # SAFETY
        # --------------------------------------------------
        safety = SafetyEvaluator.evaluate(raw_input)
        if safety.level.name == "HIGH":
            return "I can’t proceed safely."

        # --------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------
        confidence = ConfidenceEvaluator.evaluate(context)
        if confidence.level == ConfidenceLevel.LOW:
            return "I need a bit more clarity. Can you explain what you mean?"

        if confidence.level == ConfidenceLevel.CRITICAL:
            return f"I can’t proceed safely.\nReason: {confidence.reason}"

        return "I understood the request, but I don’t know how to handle it yet."

    # --------------------------------------------------
    # SAVE STATE
    # --------------------------------------------------
    def _persist(self):
        PersistenceStore.save(
            self.engine.context["data_store"],
            self.engine.context["memory"].export()
        )


def main():
    app = MLangApplication()
    app.engine.execute = app.execute
    CLI(app.engine).run()


if __name__ == "__main__":
    main()
