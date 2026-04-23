import math
from swarm_sim import algorithms
from swarm_sim import config

class Agent:
    def __init__(self, pos, vel):
        self.pos = list(pos)
        self.velocity = list(vel)
        self.radius = 6
        # detection settings
        self.detection_radius = config.DETECTION_RADIUS
        self.measurement_noise = config.MEASUREMENT_NOISE
        self.estimated_target = None

    def step(self, sim):
        # algorithm dispatcher
        # fn = getattr(algorithms, self.algorithm, algorithms.random_walk)
        new_vel = algorithms.dynamic_k_pso(self, sim)
        # apply velocity and clamp
        self.velocity = new_vel
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        # keep inside window
        w, h = sim.window_size
        self.pos[0] = max(0, min(w, self.pos[0]))
        self.pos[1] = max(0, min(h, self.pos[1]))

    def detect_and_report(self, sim):
        # detect true target if within detection radius and report direction + distance
        tx, ty = sim.target_pos
        ax, ay = self.pos
        dx = tx - ax
        dy = ty - ay
        dist = math.hypot(dx, dy)
        if dist <= self.detection_radius:
            if dist > 0:
                direction = (dx / dist, dy / dist)
            else:
                direction = (0.0, 0.0)
            # measurement noise flag exists; actual noise not implemented yet
            sim.mothership.receive_detection(self, direction, dist)

    def receive_estimated_target(self, estimated_pos, sim=None):
        # mothership-provided estimated target location
        self.estimated_target = estimated_pos
