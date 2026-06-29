class VirtualClock:
    def __init__(self):
        self.time = 0

    def now(self):
        self.time += 1
        return self.time

    def advance(self, steps=1):
        self.time += steps

