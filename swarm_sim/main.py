import pygame
import random
import math

from swarm_sim import config
from swarm_sim.agents import Agent
from swarm_sim.mothership import Mothership
from swarm_sim.evaluation import Evaluator

from swarm_sim.non_pygame import Simulation as NonPygameSimulation
from swarm_sim.pygame import Simulation as PygameSimulation


if __name__ == '__main__':
    config.USE_MOTHERSHIP = True
    for n in range(50):
        if config.USE_PYGAME:
            sim = PygameSimulation(n)
        else:
            sim = NonPygameSimulation(n)
        sim.setup(num_agents=config.NUM_AGENTS)
        sim.run()

    config.USE_MOTHERSHIP = False
    for n in range(50):
        if config.USE_PYGAME:
            sim = PygameSimulation(n)
        else:
            sim = NonPygameSimulation(n)
        sim.setup(num_agents=config.NUM_AGENTS)
        sim.run()
