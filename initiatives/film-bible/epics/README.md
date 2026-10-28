# film-bible — epics (execution order)

All done 2026-10-28; the initiative gate is Rafael's (`../film-bible.md`).

1. **contract** — field catalog (approved 2026-10-26) and the folder/Harpia contract (2 tasks)
2. **tree** — the tree panel over `bible/` (1 task)
3. **maps** — one editor per map: sets, characters, props, wardrobe (4 tasks)
4. **links** — scene ↔ set, prop detection, wardrobe ↔ character × scene, copy (4 tasks)

Cross-repository: `contract/2` starts with a `mocap-contracts` task
(`bible.harpia`). mocap-preprod agents read and propose into these records:
their registers already use stable ids, a state per item and scene
references, so the contract keeps those.
