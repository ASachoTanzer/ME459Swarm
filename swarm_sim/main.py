import pygame
import random
import math
from swarm_sim import config
from swarm_sim.agents import Agent
from swarm_sim.mothership import Mothership

class Simulation:
    def __init__(self):
        pygame.init()
        self.window_size = config.WINDOW_SIZE
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Swarm Sim — moving target + mothership')
        self.clock = pygame.time.Clock()
        self.agents = []
        self.mothership = Mothership(config.MOTHERSHIP_POS)
        self.global_signals = []
        self.target_pos = (self.window_size[0]//2, self.window_size[1]//2)
        self.max_speed = config.MAX_SPEED

    def setup(self, num_agents=20):
        w, h = self.window_size
        for i in range(num_agents):
            x = random.uniform(80, w-80)
            y = random.uniform(80, h-80)
            # start with mixed algorithms
            alg = random.choice(['random_walk', 'flock', 'seek_target'])
            a = Agent((x, y), algorithm=alg)
            self.agents.append(a)
            self.mothership.subscribe(a)

    def run(self):
        running = True
        t = 0.0
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0
            t += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.mothership.broadcast('go_seek', self)
                    elif event.key == pygame.K_2:
                        self.mothership.broadcast('go_flock', self)
                    elif event.key == pygame.K_3:
                        self.mothership.broadcast('scatter', self)

            # update moving target (circular path)
            cx, cy = self.window_size[0]//2, self.window_size[1]//2
            r = min(self.window_size)//3
            self.target_pos = (cx + math.cos(t*0.6)*r*0.5, cy + math.sin(t*0.9)*r*0.6)

            # step agents
            for a in self.agents:
                a.step(self)

            # optionally process queued global signals
            while self.global_signals:
                sig = self.global_signals.pop(0)
                # direct broadcast handled already in mothership
                pass

            # draw
            self.screen.fill(config.BG_COLOR)
            # mothership
            pygame.draw.circle(self.screen, config.MOTHERSHIP_COLOR, (int(self.mothership.pos[0]), int(self.mothership.pos[1])), 10)
            # target
            pygame.draw.circle(self.screen, pygame.Color(255, 255, 255, a=0), (int(self.target_pos[0]), int(self.target_pos[1])), 30)
            pygame.draw.circle(self.screen, config.TARGET_COLOR, (int(self.target_pos[0]), int(self.target_pos[1])), 8)
            # agents
            for a in self.agents:
                pygame.draw.circle(self.screen, config.AGENT_COLOR, (int(a.pos[0]), int(a.pos[1])), config.AGENT_RADIUS)
                #pygame.draw.line(self.screen,[255,255,255],a.pos,self.mothership.pos)
               

            # overlay text
            self._draw_info()

            pygame.display.flip()

        pygame.quit()

    def _draw_info(self):
        font = pygame.font.SysFont('Arial', 16)
        lines = [f'Agents: {len(self.agents)}', 'Keys: 1=seek 2=flock 3=scatter']
        for i, l in enumerate(lines):
            surf = font.render(l, True, (220,220,220))
            self.screen.blit(surf, (10, 10 + i*18))


if __name__ == '__main__':
    sim = Simulation()
    sim.setup(num_agents=250)
    sim.run()
