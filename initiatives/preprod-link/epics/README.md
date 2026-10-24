# preprod-link — epics (execution order)

1. **contract** — scene index and change set contracts, with the writer's export library (2 tasks)
2. **sync** — script-to-spec: snapshot and diff, the Sync to spec command, affected records (3 tasks)
3. **review** — the proposal and minutiae review view (1 task)
4. **agents** — the mocap-preprod side; tasks are planned in that repository (0 tasks here)

Needs: fountain-native/scenes/1 (scene ids), film-bible/contract/2 (bible
library), film-bible/links (scene ↔ set, prop words, wardrobe links).
Cross-repository: contract/1 and contract/2 each start with a
`mocap-contracts` task.
