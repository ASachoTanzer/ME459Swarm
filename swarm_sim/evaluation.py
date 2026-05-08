from __future__ import annotations

import csv
import math
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from swarm_sim import config

if TYPE_CHECKING:
    from main import Simulation


class Evaluator:
    """
    Computes the three Kwa swarm metrics during a simulation run.

    Call evaluator.sample(sim, t) once per simulation step, after the
    agents and target have been updated for that frame.
    """

    def __init__(self, vmax: Optional[float] = None, detection_radius: Optional[float] = None):
        self.vmax = float(vmax if vmax is not None else config.MAX_SPEED)
        self.detection_radius = float(
            detection_radius if detection_radius is not None else config.DETECTION_RADIUS
        )

        self.t: List[float] = []
        self.cvfm: List[float] = []              # instantaneous cumulative velocity fluctuation metric
        self.hbc: List[float] = []               # instantaneous mean heading-bearing correlation
        self.hbc_all: List[float] = []           # all agent-level heading-bearing correlations for histogramming
        self.tot: List[float] = []               # 1.0 when at least one agent is on target, else 0.0

    @staticmethod
    def _distance(p1: Any, p2: Any) -> float:
        return math.hypot(float(p1[0]) - float(p2[0]), float(p1[1]) - float(p2[1]))

    @staticmethod
    def _speed(v: Any) -> float:
        return math.hypot(float(v[0]), float(v[1]))

    def sample(self, sim: "Simulation", t: Optional[float] = None) -> Dict[str, float]:
        """
        Record one time-step of all three metrics.

        Returns the instantaneous values so they can also be printed or drawn
        on the pygame overlay while the simulation is running.
        """
        if t is None:
            t = float(len(self.t))

        cvfm_now = self.CVFM(sim)
        hbc_values = self.HBC_values(sim)
        hbc_now = sum(hbc_values) / len(hbc_values) if hbc_values else 0.0
        tot_now = self.ToT(sim)

        self.t.append(float(t))
        self.cvfm.append(cvfm_now)
        self.hbc.append(hbc_now)
        self.hbc_all.extend(hbc_values)
        self.tot.append(tot_now)

        return {
            "cvfm": cvfm_now,
            "hbc": hbc_now,
            "tot": tot_now,
            "time_on_target_percent_so_far": self.time_on_target_percent(),
        }

    # Cumulative Velocity Fluctuation Magnitude
    def CVFM(self, sim: "Simulation") -> float:
        """
        Instantaneous contribution to Kwa's cumulative velocity fluctuation
        magnitude:

            (1 / (N * vmax)) * sum_i ||v_i - mean(v)||

        The full run value is the time-average of this quantity, returned by
        cumulative_velocity_fluctuation_magnitude().
        """
        agents = getattr(sim, "agents", [])
        n = len(agents)
        if n == 0 or self.vmax <= 0:
            return 0.0

        mean_vx = sum(float(a.velocity[0]) for a in agents) / n
        mean_vy = sum(float(a.velocity[1]) for a in agents) / n

        fluctuation_sum = 0.0
        for a in agents:
            ux = float(a.velocity[0]) - mean_vx
            uy = float(a.velocity[1]) - mean_vy
            fluctuation_sum += math.hypot(ux, uy)

        return fluctuation_sum / (n * self.vmax)

    # Heading-Bearing Correlation
    def HBC_values(self, sim: "Simulation") -> List[float]:
        """
        Agent-level heading-bearing correlations for the current time-step.

        phi_i = dot(v_i, t_i) / ||v_i||,
        where t_i is the unit vector from agent i to the target.
        Values are in [-1, 1]. A stopped agent or an agent exactly on the
        target is assigned 0.0 to avoid division by zero.
        """
        values: List[float] = []
        target_pos = getattr(sim, "target_pos", None)
        if target_pos is None:
            return values

        for a in getattr(sim, "agents", []):
            vx = float(a.velocity[0])
            vy = float(a.velocity[1])
            speed = math.hypot(vx, vy)

            tx = float(target_pos[0]) - float(a.pos[0])
            ty = float(target_pos[1]) - float(a.pos[1])
            target_dist = math.hypot(tx, ty)

            if speed == 0.0 or target_dist == 0.0:
                values.append(0.0)
                continue

            # Unit bearing from the agent to the target
            bx = tx / target_dist
            by = ty / target_dist

            phi = (vx * bx + vy * by) / speed
            values.append(max(-1.0, min(1.0, phi)))

        return values

    def HBC(self, sim: "Simulation") -> float:
        """Instantaneous swarm-average heading-bearing correlation."""
        values = self.HBC_values(sim)
        return sum(values) / len(values) if values else 0.0

    # Time on Target
    def ToT(self, sim: "Simulation") -> float:
        """
        Instantaneous time-on-target indicator.

        Returns 1.0 if at least one agent is within detection range of the
        target during this time-step, otherwise returns 0.0.
        """
        target_pos = getattr(sim, "target_pos", None)
        if target_pos is None:
            return 0.0

        for a in getattr(sim, "agents", []):
            radius = float(getattr(a, "detection_radius", self.detection_radius))
            if self._distance(a.pos, target_pos) <= radius:
                return 1.0

        return 0.0

    def cumulative_velocity_fluctuation_magnitude(self) -> float:
        """Kwa CVFM over the full sampled run."""
        return sum(self.cvfm) / len(self.cvfm) if self.cvfm else 0.0

    def mean_heading_bearing_correlation(self) -> float:
        """Mean of all agent-level heading-bearing correlations over the run."""
        return sum(self.hbc_all) / len(self.hbc_all) if self.hbc_all else 0.0

    def time_on_target_percent(self) -> float:
        """Percent of sampled time-steps with at least one agent on target."""
        return 100.0 * sum(self.tot) / len(self.tot) if self.tot else 0.0

    def summary(self) -> Dict[str, float]:
        """Final values for comparing decentralized vs. mothership runs."""
        return {
            "samples": float(len(self.t)),
            "cvfm": self.cumulative_velocity_fluctuation_magnitude(),
            "mean_hbc": self.mean_heading_bearing_correlation(),
            "time_on_target_percent": self.time_on_target_percent(),
        }

    def reset(self) -> None:
        self.t.clear()
        self.cvfm.clear()
        self.hbc.clear()
        self.hbc_all.clear()
        self.tot.clear()

    def export_csv(self, filename: str) -> None:
        """Save time-history metrics for later plotting/reporting."""
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["t", "cvfm", "mean_hbc", "on_target"])
            for row in zip(self.t, self.cvfm, self.hbc, self.tot):
                writer.writerow(row)
