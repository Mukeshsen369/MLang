import json
import os


class PersistenceStore:
    FILE = "mlang_store.json"

    @staticmethod
    def load():
        if not os.path.exists(PersistenceStore.FILE):
            return {"data_store": {}, "user_knowledge": {}}

        with open(PersistenceStore.FILE, "r") as f:
            return json.load(f)

    @staticmethod
    def save(data_store, user_knowledge):
        payload = {
            "data_store": data_store,
            "user_knowledge": user_knowledge,
        }

        with open(PersistenceStore.FILE, "w") as f:
            json.dump(payload, f, indent=2)
