import math
from swarm_sim import algorithms
from swarm_sim import config

class Agent:
    def __init__(self, pos, vel):
        self.pos = list(pos)
        self.velocity = list(vel)
        self.radius = config.AGENT_RADIUS
        # detection settings
        self.detection_radius = config.DETECTION_RADIUS
        self.measurement_noise = config.MEASUREMENT_NOISE
        self.estimated_target = None
        self.confidence = None
        self.aR = config.AR_INIT

    def step(self, sim):
        # algorithm dispatcher
        # fn = getattr(algorithms, self.algorithm, algorithms.random_walk)
        new_vel = algorithms.dynamic_k_pso(self, sim)

        # apply velocity and move position forward by a time step
        self.velocity = new_vel
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # keep inside window
        w, h = sim.window_size
        self.pos[0] = max(0, min(w, self.pos[0]))
        self.pos[1] = max(0, min(h, self.pos[1]))

    def detect_and_report(self, sim):
        # detect true target if within detection radius and report position
        if algorithms.distance(self.pos, sim.target_pos) <= self.detection_radius:
            # tx, ty = sim.target_pos
            # sim.mothership.receive_detection(self, (tx, ty))
            sim.mothership.receive_detection(self, self.pos)

    def receive_transmission(self, estimated_pos, confidence, sim=None):
        # mothership-provided estimated target location
        self.estimated_target = estimated_pos
        self.confidence = confidence
