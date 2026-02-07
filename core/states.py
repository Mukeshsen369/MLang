from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def handle(self, engine, user_input):
        pass


class S0Ready(State):
    def handle(self, engine, user_input):
        engine.context["raw_input"] = user_input
        return engine.execute()   # 🔥 DIRECTLY EXECUTE APPLICATION LOGIC


STATE_REGISTRY = {
    "S0_READY": S0Ready(),
}
