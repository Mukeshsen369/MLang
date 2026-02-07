class KnowledgeSource:
    CORE = "core"
    USER = "user"


class Memory:
    def __init__(self):
        self.user_knowledge = {}

    # -------- Learning --------
    def learn(self, concept, definition):
        self.user_knowledge[concept.lower()] = definition

    def forget(self, concept):
        return self.user_knowledge.pop(concept.lower(), None)

    # -------- Query --------
    def get(self, concept):
        return self.user_knowledge.get(concept.lower())

    def summarize(self, concept, core_definition=None):
        result = []
        if core_definition:
            result.append((KnowledgeSource.CORE, core_definition))
        if concept.lower() in self.user_knowledge:
            result.append(
                (KnowledgeSource.USER, self.user_knowledge[concept.lower()])
            )
        return result

    # -------- Persistence --------
    def export(self):
        return self.user_knowledge

    def load(self, data):
        self.user_knowledge = data or {}
