class Mothership:
    def __init__(self, pos):
        self.pos = pos
        self.subscribers = []
        self.detections = []  # list of (agent, direction, distance)
        self.last_estimate = None

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

    def receive_detection(self, agent, direction, distance):
        # agents call this to report a direction (unit vector) and distance to target
        self.detections.append((agent, direction, distance))

    def integrate_detections(self, sim=None):
        # convert detections to estimated absolute positions and average them (weighted by confidence)
        if not self.detections:
            return None
        eps = 1e-6
        weighted_x = 0.0
        weighted_y = 0.0
        total_w = 0.0
        for agent, direction, distance in self.detections:
            ax, ay = agent.pos
            dx, dy = direction
            est_x = ax + dx * distance
            est_y = ay + dy * distance
            # weight closer detections more (simple heuristic)
            w = 1.0 / (distance + eps)
            weighted_x += est_x * w
            weighted_y += est_y * w
            total_w += w
        if total_w == 0:
            return None
        estimate = (weighted_x / total_w, weighted_y / total_w)
        self.last_estimate = estimate
        # clear detections for next timestep
        self.detections.clear()
        # broadcast estimated location to subscribers
        self.broadcast_estimated_target(estimate, sim)
        return estimate

    def broadcast_estimated_target(self, estimated_pos, sim=None):
        for s in list(self.subscribers):
            try:
                s.receive_estimated_target(estimated_pos, sim)
            except Exception:
                pass
