## 1. Agent space

- **Status:** Planned
- **Type:** code
- **Depends on:** mocap-preprod planning (the agents' space codes: one per
  agent or one shared)
- **Contract:**
  - In: an open film; a space code and owner
  - Requires: a way to register an agent in `film.json`: its id space and
    its `proposals-<code>` part, through `Film.addSpace`
    (`trelby/film.py:451`, checked by the `mocap-contracts` rules); the
    entry point (a menu, or a script for the agents' side) to be chosen
    when planned
  - Delivers: `film.json` with the agent's space and part; the folder made
- **Pre-work:** —
- **Out of scope:** reading proposals (task 2)
- **Tests:** register a space: `film.json` reads back valid with the space
  and part; a second registration of the same code is refused
