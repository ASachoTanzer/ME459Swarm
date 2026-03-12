# Swarm Sim

Simple pygame-based simulator for testing swarm robotics algorithms on a moving target with a mothership broadcaster.

Usage:

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python -m swarm_sim.main
```

Controls:
- Press `1` to broadcast `go_seek` (agents switch to seeking the target)
- Press `2` to broadcast `go_flock` (agents switch to flocking)
- Press `3` to broadcast `scatter` (agents switch to random walk)

Files:
- `main.py` — simulation loop and UI
- `agents.py` — `Agent` class (configurable `algorithm` and `receive_signal`)
- `algorithms.py` — sample algorithms: `random_walk`, `seek_target`, `flock`, `avoid_mothership`
- `mothership.py` — broadcast source
