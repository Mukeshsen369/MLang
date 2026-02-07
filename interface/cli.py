class CLI:
    def __init__(self, engine):
        self.engine = engine

    def run(self):
        print("\nMLang — Universal Human Language Interface")
        print("Type 'exit' to quit\n")

        while True:
            user = input("You: ").strip()

            if user.lower() == "exit":
                print("MLang: Goodbye.")
                break

            output = self.engine.handle(user)
            print("MLang:", output)
