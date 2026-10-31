# agent-proposals — mocap-writer

**Status:** Planned — not started. Waits for the mocap-preprod planning
(the proposal file's form and the agents' space codes).

**Goal:** the mocap-preprod agents' proposals reach the review view, through
static files only.

**Decided (Rafael, 2026-10-31):**
- **No agent on the writer side**, at least for now. The agents run only in
  mocap-preprod, as their own sessions; the writer reads what they leave
  with deterministic code: no AI, no live connection, no running process.
- **Option (a)** of the preprod-link open decision: agents write proposal
  files with Edit/Write (no Bash, no `bible propose` command) into their own
  part, `proposals-<code>` (e.g. `<film-root>/proposals/<code>/`), never
  into `bible/`.
- Each file is a `mocap-contracts` message; preferred form: a bible item
  holding only `proposal` values, under the same id as the item it proposes
  for. A new message only if that form can't carry a proposal (then a
  `mocap-contracts` task).
- The writer validates on load: an invalid file is refused and reported;
  valid proposals join the review queue by scene. Approve writes the value
  into `bible/` as `creator-approved`, by the writer; the agent's file is
  never edited.

**Scope:** registering an agent's space and part in `film.json`; the review
queue reading the `proposals-<code>` parts.

**Out of scope:** the agents themselves (mocap-preprod, planned there from
the prompt of 2026-10-31); any AI in the writer.

**Initiative gate:** on the neutral sample, a hand-written proposal file in
a registered agent part shows in Review proposals; approving it writes the
value into `bible/` as `creator-approved`; an invalid file is reported and
nothing is written.

Epics: `epics/README.md`.
