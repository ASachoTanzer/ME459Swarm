import math
from swarm_sim import algorithms

class Agent:
    def __init__(self, pos, algorithm='random_walk'):
        self.pos = list(pos)
        self.velocity = (0.0, 0.0)
        self.algorithm = algorithm
        self.radius = 6

    def step(self, sim):
        # algorithm dispatcher
        fn = getattr(algorithms, self.algorithm, algorithms.random_walk)
        new_vel = fn(self, sim)
        # apply velocity
        self.velocity = new_vel
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        # keep inside window
        w, h = sim.window_size
        self.pos[0] = max(0, min(w, self.pos[0]))
        self.pos[1] = max(0, min(h, self.pos[1]))

    def receive_signal(self, signal, sim):
        # Example: switch algorithm based on mothership signal
        if signal == 'go_seek':
            self.algorithm = 'seek_target'
        elif signal == 'go_flock':
            self.algorithm = 'flock'
        elif signal == 'scatter':
            self.algorithm = 'random_walk'
