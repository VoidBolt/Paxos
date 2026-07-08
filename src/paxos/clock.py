class VirtualClock:
    def __init__(self):
        self.time = 0

    def now(self):
        self.advance()
        return self.time

    def advance(self, steps=1):
        self.time += steps

