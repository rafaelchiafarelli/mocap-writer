# workflow-link — mocap-writer

**Status:** Planned — not started (Rafael, 2026-10-31).

**Goal:** the creator decides the pre-production agents' proposals in the
writer. The agents leave proposals and requests in the film's workflow
database (`workflow.sqlite`, `mocap-contracts` `workflow-records`); the
writer lists them in its review view, records each decision there, and
writes approved values into the bible itself.

**Decided (Rafael, 2026-10-31):**
- No agent on the writer side, no live connection: the writer reads and
  writes the database file with `mocap_contracts.db`, plain code.
- Agents never write into `bible/`. Approving is the writer's write:
  `creator-approved`, through `Film.writeText`, logged in the history.
- A rejection is a review record, so the agent sees it and doesn't propose
  the value again; the agent's proposal itself is never edited.
- One id space per agent. Agents never create bible items or scene links:
  they ask the creator with a request.
- One program writes at a time (one creator for now).

**Keep in mind** (from preprod-link, 2026-10-24): a small decision must be
cheap: proposals grouped by scene, batches from the keyboard, a decided
value not reopened unless its source changed.

**Scope:** registering an agent's space and the `workflow` part; open
proposals in the review queue; reviews written on approve, reject and
edit; requests addressed to the creator.

**Out of scope:** the agents and their MCP tool (`mocap-preprod`
`preprod-link`); which version of the script a proposal answers
(`versioning`); the worklist and the decision register.

**Needs:** `mocap-contracts` `v0.8.0` (`workflow-records`).

**Initiative gate:** on the neutral sample with a test database holding
proposals from two agents and a request to the creator: the review view
lists them by scene; one approved lands in the bible as
`creator-approved` with a history line; one rejected leaves the bible
untouched and has its review; the request is answered from the writer.

Epics: `review` (4 tasks, in order).
