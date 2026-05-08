import random
import math
from swarm_sim import config


def clamp(vec, max_len):
    x, y = vec
    mag = math.hypot(x, y)
    if mag > max_len and mag > 0:
        return (x / mag * max_len, y / mag * max_len)
    return vec


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def k_nearest(agent, agents, k):
    others = [a for a in agents if a is not agent]
    others.sort(key=lambda a: distance(a.pos, agent.pos))
    return others[:max(0, min(k, len(others)))]


def adaptive_repulsion_update(sim, agent, neighbors):
    """
    Update global adaptive repulsion coefficient `sim.aR` according to Algorithm 1.
    If the agent or any neighbor detects the target (f == -1), decrease aR, else increase.
    """
    # f(x_i,t) == -1 if agent within detection radius of true target
    def detects(a):
        return distance(a.pos, sim.target_pos) <= a.detection_radius

    any_detect = detects(agent) or any(detects(n) for n in neighbors)
    if any_detect:
        if agent.aR > config.AR_MIN:
            agent.aR = max(config.AR_MIN, agent.aR - config.AR_DELTA)
    else:
        if agent.aR < config.AR_MAX:
            agent.aR = min(config.AR_MAX, agent.aR + config.AR_DELTA)


def v_repulsion(agent, neighbors, sim):
    """Compute v_rep for agent using Eq. (3).

    v_rep = - sum_j aR * r_vec / r^(d+1)
    where r_vec = pos_j - pos_i, r = |r_vec|, d = config.AR_D
    """
    rep_wall_x, rep_wall_y = wall_repulsion(agent,sim)
    ax = ay = 0.0
    dpow = config.AR_D
    aR = agent.aR
    for n in neighbors:
        rx = n.pos[0] - agent.pos[0]
        ry = n.pos[1] - agent.pos[1]
        r = math.hypot(rx, ry)
        if r == 0:
            continue
        # contribution: - aR * (r_vec) / r^(d+1)
        factor = -aR**dpow / (r ** (dpow + 1))
        ax += factor * rx
        ay += factor * ry
    return (ax + rep_wall_x, ay + rep_wall_y)


def wall_repulsion(agent, sim):
    """Repel agent from simulation walls when within WALL_MARGIN.

    Returns a vector pushing agent away from nearby walls.
    """
    margin = config.WALL_MARGIN
    strength = config.WALL_STRENGTH
    x, y = agent.pos
    w, h = sim.window_size
    wx = wy = 0.0
    # left wall
    if x < margin and x > 0:
        r = max(x, 1e-4)
        wx += strength * (1.0 / (r ** config.AR_D))
    # right wall
    if x > (w - margin):
        r = max(w - x, 1e-4)
        wx -= strength * (1.0 / (r ** config.AR_D))
    # top wall
    if y < margin and y > 0:
        r = max(y, 1e-4)
        wy += strength * (1.0 / (r ** config.AR_D))
    # bottom wall
    if y > (h - margin):
        r = max(h - y, 1e-4)
        wy -= strength * (1.0 / (r ** config.AR_D))
    return (wx, wy)


def vpso_component(agent, nbest_pos):
    """Compute PSO velocity component using Eq. (1)

    vpso = omega * v + c * r * (Nbest - x)
    """
    vx, vy = agent.velocity
    rx = random.random()
    dx = nbest_pos[0] - agent.pos[0]
    dy = nbest_pos[1] - agent.pos[1]
    comp_x = config.OMEGA * vx + config.PSO_C * rx * dx
    comp_y = config.OMEGA * vy + config.PSO_C * rx * dy
    return (comp_x, comp_y)


def v_mothership(agent, sim):
    """Compute velocity component for moving towards mothership's estimated target."""
    if agent.estimated_target is None:
        return (0.0, 0.0)
    
    tx, ty = agent.estimated_target
    ax, ay = agent.pos
    dx = config.MOTHERSHIP_STRENGTH*agent.confidence*(tx - ax)
    dy = config.MOTHERSHIP_STRENGTH*agent.confidence*(ty - ay)
    return (dx, dy)


def dynamic_k_pso(agent, sim):
    """Main update implementing Algorithm 2 for a single agent.

    Returns the new velocity vector for the agent.
    """
    # determine topological k-nearest neighbors
    neighbors = k_nearest(agent, sim.agents, config.K_NEIGHBORS)

    # determine Nbest
    def detects(a):
        return distance(a.pos, sim.target_pos) <= a.detection_radius

    if detects(agent):
        nbest = agent.pos
    else:
        target_neighbor = None
        for n in neighbors:
            if detects(n):
                target_neighbor = n
                break
        if target_neighbor is not None:
            nbest = target_neighbor.pos
        else:
            nbest = agent.pos

    # vpso
    vpso = vpso_component(agent, nbest)

    # adaptive repulsion update using Algorithm 1 (updates sim.aR)
    adaptive_repulsion_update(sim, agent, neighbors)

    # vrep
    vrep = v_repulsion(agent, neighbors, sim)

    # combine
    vx = vpso[0] + vrep[0]
    vy = vpso[1] + vrep[1]

    # clamp to V_MAX
    return clamp((vx, vy), config.V_MAX)
