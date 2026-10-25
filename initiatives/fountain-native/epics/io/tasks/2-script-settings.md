## 2. Per-script settings with a Fountain script

- **Type:** code
- **Depends on:** io/1
- **Decision (Rafael, 2026-10-25):** a **sidecar file** next to the script,
  for now; a richer format (Fountain extended with Mocap Studio's own
  parts) may replace it later. Waiting on the same conversation: whether
  the writer's own file, not the Fountain, becomes the source of truth;
  if so this task changes.
- **Problem:** a `.trelby` file carries per-script settings: page setup and
  element styles (`Config`), auto-completion lists, locations, the script's
  spell-checker words, page headers. Fountain has no place for them, so
  after io/1 a `.fountain` opens with defaults and none of them is saved.
- **Options (to decide):**
  1. a sidecar file next to the script (`<name>.fountain.writer` or a
     folder in the film root), in Trelby's `key:value` form;
  2. a boneyard block at the end of the `.fountain`
     (`/* mocap-writer settings ... */`): one file, other tools ignore it;
  3. global settings only: the film's page setup lives in the global
     config, lists are rebuilt from the script, headers stay default.
- **Contract (after the decision):**
  - In: a `.fountain` script and its settings in the chosen place
  - Requires: open restores them, save writes them, the Fountain text
    itself is still byte-identical after open → save
  - Delivers: settings that survive the round trip
- **Pre-work:** the decision (recorded above); the sidecar's name and
  form, to propose and confirm
- **Tests:** settings changed → saved → reopened equal; the script text
  unchanged
