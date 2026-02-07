from domains.base import Domain, DomainResponse
from external.eki import ExternalKnowledgeInterface, ExternalKnowledgeRequest


class KnowledgeDomain(Domain):
    name = "KNOWLEDGE"

    def __init__(self):
        self.core_knowledge = {
            "gravity": "Gravity is the force that attracts objects with mass toward each other.",
            "mean": "Mean is the average obtained by dividing the sum of values by their count.",
            "speed": "Speed is the distance traveled per unit of time.",
            "force": "Force is an interaction that changes the motion of an object.",
            "energy": "Energy is the capacity to do work."
        }
        self.eki = ExternalKnowledgeInterface()

    def can_handle(self, context):
        text = context.get("raw_input", "").lower()
        return (
            text.startswith((
                "what is", "explain", "define",
                "tell me about", "what do you know about", "forget"
            ))
            or context.get("pending_external")
        )

    def handle(self, context):
        memory = context["memory"]
        raw = context.get("raw_input", "").strip().lower()

        # ---------- Follow-up answer ----------
        if context.get("pending_external"):
            answer = raw
            concept = context.pop("pending_external")

            if answer in {"yes", "y", "sure", "ok"}:
                result = self.eki.fetch(
                    ExternalKnowledgeRequest(concept=concept)
                )

                if not result.summaries:
                    return DomainResponse(True, "External information unavailable.")

                lines = [f"External information on '{concept}':\n"]
                for s in result.summaries:
                    lines.append(f"• {s}")
                lines.append(f"\nConfidence: {result.confidence}")

                return DomainResponse(True, "\n".join(lines))

            return DomainResponse(True, "Alright. I won’t use external information.")

        # ---------- Forget ----------
        if raw.startswith("forget"):
            concept = raw.replace("forget", "", 1).strip()
            if memory.forget(concept):
                return DomainResponse(True, f"I’ve forgotten {concept}.")
            return DomainResponse(True, f"I don’t have anything stored for {concept}.")

        # ---------- Extract ----------
        concept = self._extract(raw)
        if not concept:
            return DomainResponse(True, needs_clarification=True)

        # ---------- User knowledge ----------
        user_def = memory.get(concept)
        if user_def:
            return DomainResponse(True, f"{concept}: {user_def}")

        # ---------- Core knowledge ----------
        if concept in self.core_knowledge:
            return DomainResponse(True, self.core_knowledge[concept])

        # ---------- Unknown ----------
        context["pending_external"] = concept
        return DomainResponse(
            True,
            f"I don’t have internal knowledge about '{concept}'. "
            f"Do you want me to look it up using external sources?"
        )

    def _extract(self, text):
        for p in (
            "what is", "explain", "define",
            "tell me about", "what do you know about"
        ):
            if text.startswith(p):
                return text.replace(p, "", 1).strip()
        return None
