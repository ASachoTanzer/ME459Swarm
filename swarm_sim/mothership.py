class Mothership:
    def __init__(self, pos):
        self.pos = pos
        self.subscribers = []
        self.detections = []  # list of (agent, direction, distance)
        self.confidence = 0.0
        self.x_estimate, self.y_estimate = None, None
        self.last_estimate = None

    def subscribe(self, agent):
        if agent not in self.subscribers:
            self.subscribers.append(agent)

    def unsubscribe(self, agent):
        if agent in self.subscribers:
            self.subscribers.remove(agent)

    def receive_detection(self, agent, position):
        # agents call this to report a direction (unit vector) and distance to target
        self.detections.append((agent, position))

    def integrate_detections(self, sim=None):
        # convert detections to estimated absolute positions and average them (weighted by confidence)
        if not self.detections:
            self.confidence *= 0.995  # decay confidence if no detections
        else:
            self.confidence = 1
            x_estimate, y_estimate = 0.0, 0.0
            for i in self.detections:
                x_estimate += i[1][0]
                y_estimate += i[1][1]
            x_estimate /= len(self.detections)
            y_estimate /= len(self.detections)
            self.x_estimate, self.y_estimate = x_estimate, y_estimate

        self.detections = []  # clear detections after integration
        
        self.broadcast_estimated_target()

    def broadcast_estimated_target(self, sim=None):
        print(f"Mothership broadcasting estimate: ({self.x_estimate:.2f}, {self.y_estimate:.2f}) with confidence {self.confidence:.2f}")
        for s in list(self.subscribers):
            try:
                s.receive_transmission((self.x_estimate, self.y_estimate), self.confidence, sim)
            except Exception:
                pass
