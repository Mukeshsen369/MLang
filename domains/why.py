from domains.base import Domain, DomainResponse


class WhyDomain(Domain):
    name = "WHY"

    def can_handle(self, context):
        raw = context["raw_input"].lower().strip()
        return raw == "why" or raw.startswith("why ")

    def handle(self, context):
        last = context.get("last_decision")

        if not last:
            return DomainResponse(
                True,
                "There is no recent decision to explain."
            )

        return DomainResponse(
            True,
            last.get("reason", "I made that decision based on available information.")
        )
