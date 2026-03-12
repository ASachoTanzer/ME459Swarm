class Mothership:
    def __init__(self, pos):
        self.pos = pos
        self.subscribers = []

    def subscribe(self, agent):
        if agent not in self.subscribers:
            self.subscribers.append(agent)

    def unsubscribe(self, agent):
        if agent in self.subscribers:
            self.subscribers.remove(agent)

    def broadcast(self, signal, sim=None):
        # place signal in sim global list (for optionally delayed handling)
        if sim is not None:
            sim.global_signals.append(signal)
        # Also notify directly
        for s in list(self.subscribers):
            try:
                s.receive_signal(signal, sim)
            except Exception:
                pass
