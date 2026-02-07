from core.states import STATE_REGISTRY
import copy


class Engine:
    def __init__(self):
        self.current_state = STATE_REGISTRY["S0_READY"]
        self.context = {}

    def handle(self, user_input):
        return self.current_state.handle(self, user_input)

    # ---------------- UNDO ----------------
    def undo(self, steps=1):
        history = self.context.get("history", [])
        future = self.context.get("future", [])

        if not history:
            return "There is nothing to undo."

        steps = max(1, steps)
        actual = min(steps, len(history))

        for _ in range(actual):
            snapshot = history.pop()
            future.append({
                "data_store": copy.deepcopy(self.context["data_store"]),
                "user_knowledge": copy.deepcopy(
                    self.context["memory"].export()
                ),
                "description": snapshot["description"]
            })

            self.context["data_store"] = snapshot["data_store"]
            self.context["memory"].load(snapshot["user_knowledge"])

        self.context.pop("last_decision", None)
        return f"Undid {actual} action(s)."

    # ---------------- REDO ----------------
    def redo(self, steps=1):
        future = self.context.get("future", [])
        history = self.context.get("history", [])

        if not future:
            return "There is nothing to redo."

        steps = max(1, steps)
        actual = min(steps, len(future))

        for _ in range(actual):
            snapshot = future.pop()
            history.append({
                "data_store": copy.deepcopy(self.context["data_store"]),
                "user_knowledge": copy.deepcopy(
                    self.context["memory"].export()
                ),
                "description": snapshot["description"]
            })

            self.context["data_store"] = snapshot["data_store"]
            self.context["memory"].load(snapshot["user_knowledge"])

        self.context.pop("last_decision", None)
        return f"Redid {actual} action(s)."

    # 🔑 THIS WILL BE OVERRIDDEN BY main.py
    def execute(self):
        return "Execution completed."
