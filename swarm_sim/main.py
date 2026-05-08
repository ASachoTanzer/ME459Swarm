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
        if config.USE_MOTHERSHIP:
            self.mothership = Mothership(config.MOTHERSHIP_POS)
        self.global_signals = []
        self.target_pos = (self.window_size[0]//2, self.window_size[1]//2)
        self.max_speed = config.MAX_SPEED
        # adaptive repulsion coefficient (updated by algorithms)

    def setup(self, num_agents=20):
        w, h = self.window_size
        for i in range(num_agents):
            x = random.uniform(80, w-80)
            y = random.uniform(80, h-80)
            # start with mixed algorithms
            vx = random.uniform(-self.max_speed, self.max_speed)
            vy = random.uniform(-self.max_speed, self.max_speed)
            a = Agent((x, y), (vx, vy))
            self.agents.append(a)
            if config.USE_MOTHERSHIP:
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
                    pass
                    # if event.key == pygame.K_1:
                    #     self.mothership.broadcast('go_seek', self)
                    # elif event.key == pygame.K_2:
                    #     self.mothership.broadcast('go_flock', self)
                    # elif event.key == pygame.K_3:
                    #     self.mothership.broadcast('scatter', self)

            # update moving target (circular path)
            cx, cy = self.window_size[0]//2, self.window_size[1]//2
            r = min(self.window_size)//3
            self.target_pos = (cx + math.cos(t*0.6)*r*0.5, cy + math.sin(t*0.9)*r*0.6)

            # detection phase: agents detect target (if within range) and report to mothership
            if config.USE_MOTHERSHIP:
                for a in self.agents:
                    try:
                        a.detect_and_report(self)
                    except Exception:
                        pass

                # mothership integrates reports and broadcasts estimated target
                try:
                    self.mothership.integrate_detections(self)
                except Exception:
                    pass

            # step agents (they may use mothership-provided estimate)
            for a in self.agents:
                a.step(self)

            if config.CAMERA_FOLLOW:
                offset = (int(self.target_pos[0] - self.screen.get_width()/2), int(self.target_pos[1]- self.screen.get_height()/2))
            else:
                offset = (0,0)

            # optionally process queued global signals
            # while self.global_signals:
            #     sig = self.global_signals.pop(0)
            #     # direct broadcast handled already in mothership
            #     pass

            # draw
            self.screen.fill(config.BG_COLOR)
            if config.USE_MOTHERSHIP:
                # mothership
                pygame.draw.circle(self.screen, config.MOTHERSHIP_COLOR, (int(self.mothership.pos[0] - offset[0]), int(self.mothership.pos[1] - offset[0])), 10)
            # target
            pygame.draw.circle(self.screen, pygame.Color(255, 255, 255, a=0), (int(self.target_pos[0] - offset[0]), int(self.target_pos[1] - offset[1])), config.DETECTION_RADIUS)
            pygame.draw.circle(self.screen, config.TARGET_COLOR, (int(self.target_pos[0] - offset[0]), int(self.target_pos[1] - offset[1])), 8)
            # agents
            for a in self.agents:
                pygame.draw.circle(self.screen, config.AGENT_COLOR, (int(a.pos[0]- offset[0]), int(a.pos[1]- offset[1])), config.AGENT_RADIUS)
                #pygame.draw.line(self.screen,[255,255,255],a.pos,self.mothership.pos)
               

            # overlay text
            self._draw_info()

            pygame.display.flip()

        pygame.quit()

    def _draw_info(self):
        pass
        """font = pygame.font.SysFont('Arial', 16)
        lines = [f'Agents: {len(self.agents)}', 'Keys: 1=seek 2=flock 3=scatter']
        for i, l in enumerate(lines):
            surf = font.render(l, True, (220,220,220))
            self.screen.blit(surf, (10, 10 + i*18))"""





if __name__ == '__main__':
    sim = Simulation()
    sim.setup(num_agents=config.NUM_AGENTS)
    sim.run()
