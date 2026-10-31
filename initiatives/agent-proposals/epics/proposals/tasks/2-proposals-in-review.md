## 2. Proposals in the review queue

- **Status:** Planned
- **Type:** code (and UI in the review view)
- **Depends on:** task 1; mocap-preprod planning (the proposal file's form;
  a new `mocap-contracts` message if a proposal-only bible item is not
  enough)
- **Contract:**
  - In: `<film-root>/<proposals-<code> part>/` files written by agents
  - Requires: `review.queue` also lists the values of every
    `proposals-<code>` part, by scene, marked with their agent; an invalid
    file is refused and reported as a film notice, never repaired; approve
    writes the value into the bible item as `creator-approved` (the
    writer's write, logged), reject or edit as today; the agent's file is
    never written by the writer
  - Delivers: agents' proposals reviewable in Script → Review proposals
- **Pre-work:** a neutral proposal fixture in the agreed form
- **Out of scope:** any AI or agent run from the writer
- **Tests:** a fixture proposal shows in the queue under its scene;
  approve writes `creator-approved` into `bible/` and leaves the agent's
  file unchanged; an invalid file is reported and changes nothing
