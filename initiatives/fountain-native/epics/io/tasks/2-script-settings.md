## 2. Per-script settings with a Fountain script

- **Status:** Planned — re-planned after the file-format decision
  (option A, 2026-10-25): the settings are a record in the film root.

- **Type:** code
- **Depends on:** io/1; file-format/layout/1 (root index, part
  ownership); a `mocap-contracts` task for a `script_settings` message,
  done and tagged
- **Decision (Rafael, 2026-10-25):** first a sidecar file next to the
  script; **replaced** the same day by the file-format decision (option A):
  the settings are a Harpia message, a part of the film root listed in
  `film.json` and owned by the writer.
- **Problem:** a `.trelby` file carries per-script settings: page setup and
  element styles (`Config`), auto-completion lists, locations, the script's
  spell-checker words, page headers. Fountain has no place for them, so
  after io/1 a `.fountain` opens with defaults and none of them is saved.
- **Contract:**
  - In: a `.fountain` script and its settings record in the film root
  - Requires: open restores them, save writes them as a `script_settings`
    message in the part `film.json` lists for them; the Fountain text
    itself is still byte-identical after open → save; a script opened
    outside a film root opens with defaults, as today
  - Delivers: settings that survive the round trip
- **Pre-work:** the `mocap-contracts` task above; the record's fields
  (the `Config` and lists named in Problem), to propose and confirm
- **Tests:** settings changed → saved → reopened equal; the script text
  unchanged
