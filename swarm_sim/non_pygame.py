import random
import math
import time

from swarm_sim import config
from swarm_sim.agents import Agent
from swarm_sim.mothership import Mothership
from swarm_sim.evaluation import Evaluator


class Simulation:
    def __init__(self, id):
        self.id = id
        self.window_size = config.WINDOW_SIZE
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

    def setup(self, num_agents=None):
        if num_agents is None:
            num_agents = getattr(config, 'NUM_AGENTS', 20)
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

    def run(self, dt=None, progress_every: float = None):
        """Run the simulation headless.

        - `dt`: simulated timestep (seconds). If None, uses `config.DT` or 0.017s.
        - `progress_every`: if set, prints progress every `progress_every` simulated seconds.
        """
        t = 0.0
        dt = 0.017
        last_print = 0.0

        while t < config.SIM_TIME:
            t += dt

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

            if progress_every and (t - last_print) >= progress_every:
                print(f"Sim {self.id}: t={t:.2f}/{config.SIM_TIME}")
                last_print = t

        # Done: save metrics
        self._print_and_save_metrics()

    def _print_and_save_metrics(self):
        summary = self.evaluator.summary()
        mode = 'mothership' if config.USE_MOTHERSHIP else 'decentralized'
        filename = f'./results/swarm_metrics_{mode}_{self.id}.csv'

        print('\nKwa metric summary')
        print(f'Mode: {mode}')
        print(f'Samples: {int(summary["samples"]) }')
        print(f'Cumulative velocity fluctuation magnitude: {summary["cvfm"]:.6f}')
        print(f'Mean heading-bearing correlation: {summary["mean_hbc"]:.6f}')
        print(f'Time on target: {summary["time_on_target_percent"]:.2f}%')

        try:
            self.evaluator.export_csv(filename)
            print(f'Saved metric history to {filename}')
        except OSError as e:
            print(f'Could not save metric history CSV: {e}')
