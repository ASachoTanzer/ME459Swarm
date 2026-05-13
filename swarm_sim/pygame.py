import pygame
import random
import math

from swarm_sim import config
from swarm_sim.agents import Agent
from swarm_sim.mothership import Mothership
from swarm_sim.evaluation import Evaluator


class Simulation:
    def __init__(self, id):
        self.id = id
        pygame.init()
        self.window_size = config.WINDOW_SIZE
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Swarm Sim — moving target + mothership')
        self.clock = pygame.time.Clock()
        self.agents = []

        if config.USE_MOTHERSHIP:
            self.mothership = Mothership(config.MOTHERSHIP_POS)

        self.global_signals = []
        self.target_pos = (self.window_size[0] // 2, self.window_size[1] // 2)
        self.max_speed = config.MAX_SPEED

        # Kwa metric evaluator: CVFM, heading-bearing correlation, and time on target
        self.evaluator = Evaluator(
            vmax=self.max_speed,
            detection_radius=config.DETECTION_RADIUS,
        )
        self.latest_metrics = {
            "cvfm": 0.0,
            "hbc": 0.0,
            "tot": 0.0,
            "time_on_target_percent_so_far": 0.0,
        }

    def setup(self, num_agents=20):
        w, h = self.window_size
        for _ in range(num_agents):
            x = random.uniform(80, w - 80)
            y = random.uniform(80, h - 80)
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

            # Update moving target on a circular/elliptical path
            cx, cy = self.window_size[0] // 2, self.window_size[1] // 2
            r = min(self.window_size) // 3
            self.target_pos = (
                cx + math.cos(t * 0.6) * r * 0.5,
                cy + math.sin(t * 0.9) * r * 0.6,
            )

            # Detection phase: agents detect target and report to mothership
            if config.USE_MOTHERSHIP:
                for a in self.agents:
                    try:
                        a.detect_and_report(self)
                    except Exception:
                        pass

                # Mothership integrates reports and broadcasts estimated target
                try:
                    self.mothership.integrate_detections(self)
                except Exception:
                    pass

            # Step agents. They may use a mothership-provided estimate.
            for a in self.agents:
                a.step(self)

            # Record Kwa metrics once per simulation frame, after target and agent updates.
            self.latest_metrics = self.evaluator.sample(self, t)
            if config.CAMERA_FOLLOW:
                offset = (int(self.target_pos[0] - self.screen.get_width()/2), int(self.target_pos[1]- self.screen.get_height()/2))
            else:
                offset = (0,0)

            # Draw
            self.screen.fill(config.BG_COLOR)

            if config.USE_MOTHERSHIP:
                pygame.draw.circle(
                    self.screen,
                    config.MOTHERSHIP_COLOR,
                    (
                        int(self.mothership.pos[0] - offset[0]),
                        int(self.mothership.pos[1] - offset[1]),
                    ),
                    10,
                )

            # Target detection radius and target center
            pygame.draw.circle(
                self.screen,
                pygame.Color(255, 255, 255, a=0),
                (int(self.target_pos[0] - offset[0]), int(self.target_pos[1] - offset[1])),
                config.DETECTION_RADIUS,
            )
            pygame.draw.circle(
                self.screen,
                config.TARGET_COLOR,
                (int(self.target_pos[0] - offset[0]), int(self.target_pos[1] - offset[1])),
                8,
            )

            # Agents
            for a in self.agents:
                pygame.draw.circle(
                    self.screen,
                    config.AGENT_COLOR,
                    (int(a.pos[0] - offset[0]), int(a.pos[1] - offset[1])),
                    config.AGENT_RADIUS,
                )
                # pygame.draw.line(self.screen, [255, 255, 255], a.pos, self.mothership.pos)

            self._draw_info()
            pygame.display.flip()

            if t >= config.SIM_TIME:
                running = False

        self._print_and_save_metrics()
        pygame.quit()

    def _draw_info(self):
        font = pygame.font.SysFont('Arial', 16)
        summary = self.evaluator.summary()
        mode = 'Mothership' if config.USE_MOTHERSHIP else 'Decentralized'

        lines = [
            f'Mode: {mode}',
            f'Agents: {len(self.agents)}',
            f'CVFM now/run: {self.latest_metrics["cvfm"]:.3f} / {summary["cvfm"]:.3f}',
            f'HBC now/run: {self.latest_metrics["hbc"]:.3f} / {summary["mean_hbc"]:.3f}',
            f'Time on target: {summary["time_on_target_percent"]:.1f}%',
        ]

        for i, line in enumerate(lines):
            surf = font.render(line, True, (220, 220, 220))
            self.screen.blit(surf, (10, 10 + i * 18))

    def _print_and_save_metrics(self):
        summary = self.evaluator.summary()
        mode = 'mothership' if config.USE_MOTHERSHIP else 'decentralized'
        filename = f'./results/swarm_metrics_{mode}_{self.id}.csv'

        print('\nKwa metric summary')
        print(f'Mode: {mode}')
        print(f'Samples: {int(summary["samples"])}')
        print(f'Cumulative velocity fluctuation magnitude: {summary["cvfm"]:.6f}')
        print(f'Mean heading-bearing correlation: {summary["mean_hbc"]:.6f}')
        print(f'Time on target: {summary["time_on_target_percent"]:.2f}%')

        try:
            self.evaluator.export_csv(filename)
            print(f'Saved metric history to {filename}')
        except OSError as e:
            print(f'Could not save metric history CSV: {e}')