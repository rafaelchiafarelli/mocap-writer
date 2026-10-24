# preprod-link — mocap-writer

**Status:** Planned — not started. Comes after film-bible (Rafael, 2026-10-24).

**Goal:** the writer feeds the mocap-preprod agents with structured,
trustworthy data, and keeps that data current while the script keeps
changing. The script is never closed or locked: Rafael writes, presses
**Sync to spec**, and the writer works out what changed and which records and
agent work it affects.

**Decided (Rafael, 2026-10-24):**
- **No agent writes prompts for other agents.** Everything that can be
  derived from the script and the bible is produced by deterministic code
  (scene index, change set, bible records); the agents' own definitions in
  `mocap-preprod/.claude/agents/` stay the fixed prompt templates. AI is used
  only where judgment is needed, and that is the specialists' job already.
  Reasons: value states (`proposal` vs `creator-approved`) pass through code
  untouched, the output is testable, and no extra hosted-agent cost.
- **Iterative, never a one-shot hand-off.** Script-to-spec runs again on every
  sync and reports the difference against the last sync.
- The link goes through files in the film root whose format is a Harpia
  contract (`mocap-contracts`), read and written with `mocap_contracts`.

**Keep in mind (Rafael, 2026-10-24):** most of the creator's time goes into
deciding the minutiae of what is in a scene, far more than story problems.
That is accepted for now, but every task here should make a small decision
cheap: open questions grouped by scene, approve/reject in batches from the
keyboard, a value decided once on an item applies to every scene unless a
scene overrides it, and a sync never reopens a decision whose source did not
change.

**Scope:** the scene index and change set contracts; script-to-spec (snapshot,
diff, affected records) behind a Sync to spec command; a review view for agent
proposals and open minutiae; the writer side of the agents' read/propose path.

**Out of scope:** the bible itself (film-bible); changing the agents
(planned as `mocap-preprod` tasks, see `epics/agents/`); launching agents and
filling their invocation prompts (`mocap-dashboard`); generating images (an
AI job that would need its own agent, license check and local-vs-hosted
measurement); story structure (story-structure).

**Open decision (deferred to the mocap-preprod planning):** how agents write
proposals. (a) they write `item.json` with their Edit/Write tools and the
writer refuses an invalid file on load; (b) they get Bash and a small
validating `bible propose` command. Reading needs neither, so it doesn't
block the contract, sync or review epics.

**Initiative gate:** on the neutral sample, Rafael edits the script (adds a
scene, moves one, renames a character, adds a prop word), presses Sync to
spec, sees exactly those changes and the affected records, approves a batch
of proposals in the review view, and a mocap-preprod specialist run on the
sample reads the scene index and bible and cites their ids.

Epics: `epics/README.md`.
