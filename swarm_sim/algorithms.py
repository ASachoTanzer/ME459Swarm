import random
import math
from swarm_sim import config

def clamp(vec, max_len):
    x, y = vec
    mag = math.hypot(x, y)
    if mag > max_len and mag > 0:
        return (x / mag * max_len, y / mag * max_len)
    return vec

def random_walk(agent, sim):
    # small random jitter
    ax = (random.random() - 0.5) * 0.6
    ay = (random.random() - 0.5) * 0.6
    vx, vy = agent.velocity
    vx += ax
    vy += ay
    return clamp((vx, vy), sim.max_speed)

def seek_target(agent, sim):
    # prefer mothership-provided estimate if available
    if getattr(agent, 'estimated_target', None) is not None:
        tx, ty = agent.estimated_target
    else:
        tx, ty = sim.target_pos
    ax, ay = agent.pos
    dx = tx - ax
    dy = ty - ay
    dist = math.hypot(dx, dy)
    if dist >= agent.detection_radius:
        ax = (random.random() - 0.5) * 0.6
        ay = (random.random() - 0.5) * 0.6
        vx, vy = agent.velocity
        vx += ax
        vy += ay
        return clamp((vx, vy), sim.max_speed)
    desired = (dx / dist * sim.max_speed, dy / dist * sim.max_speed)
    vx, vy = agent.velocity

    #steering = desired - velocity (simple)
    steer = (desired[0] - vx, desired[1] - vy)
    return clamp((vx + steer[0]*0.05, vy + steer[1]*0.05), sim.max_speed)

def avoid_mothership(agent, sim):
    mx, my = sim.mothership.pos
    ax, ay = agent.pos
    dx = ax - mx
    dy = ay - my
    dist = math.hypot(dx, dy)
    if dist == 0:
        return agent.velocity
    if dist < 80:
        # move away strongly
        return clamp((dx/dist*sim.max_speed, dy/dist*sim.max_speed), sim.max_speed)
    return agent.velocity

def flock(agent, sim):
    # simple Reynolds rules: cohesion + separation + alignment
    neighbors = [a for a in sim.agents if a is not agent and distance(a.pos, agent.pos) < 60]
    vx, vy = agent.velocity
    if not neighbors:
        return random_walk(agent, sim)
    # cohesion: move toward average pos
    avgx = sum(a.pos[0] for a in neighbors) / len(neighbors)
    avgy = sum(a.pos[1] for a in neighbors) / len(neighbors)
    cx = (avgx - agent.pos[0]) * 0.002
    cy = (avgy - agent.pos[1]) * 0.002
    # separation
    sx = 0
    sy = 0
    for a in neighbors:
        d = distance(a.pos, agent.pos)
        if d < 18 and d>0:
            sx -= (a.pos[0]-agent.pos[0]) * 0.02
            sy -= (a.pos[1]-agent.pos[1]) * 0.02
    # alignment
    avvx = sum(a.velocity[0] for a in neighbors) / len(neighbors)
    avvy = sum(a.velocity[1] for a in neighbors) / len(neighbors)
    ax_adj = (avvx - vx) * 0.05
    ay_adj = (avvy - vy) * 0.05
    nx = vx + cx + sx + ax_adj
    ny = vy + cy + sy + ay_adj
    return clamp((nx, ny), sim.max_speed)

def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])
