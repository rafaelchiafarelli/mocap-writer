## 3. Options and recommendation

- **Status:** Done (2026-10-25) — Rafael chose A

- **Type:** study (no code); Rafael decides
- **Depends on:** 2
- **Contract:**
  - In: the comparison of task 2
  - Requires: two or three options, each with what it costs, what it breaks
    in the decisions listed in `../../file-format.md`, and the order of the
    work it implies; one recommendation with its reasons
  - Delivers: Rafael's decision, recorded here with the date, and the list
    of tasks to re-plan (film-bible contract/2, fountain-native io/2,
    preprod-link contract/1 and 2)
- **Pre-work:** —
- **Out of scope:** implementation
- **Tests:** —

### Options put to Rafael (2026-10-25)
- **A. Folder of Harpia JSON records, ISOXML-style** — cheapest, readable,
  syncs with any file sync; needs its own history design.
- **C. Change log in SQLite** (recommended for scale) — history and team
  sync built in; costs a `dump` tool to stay readable, and more design.
- B, D and E: see task 2.

### Decision (Rafael, 2026-10-25)
**Lock in A; keep C in mind.** A is built now. It is designed so that
moving to C later is a migration, not a redesign: every record is a Harpia
message, ids are typed and stable with a separate id space per writer or
agent, nothing refers to a file path, and a change can be written down as
a message.

What it changes in earlier decisions:
- film-bible "folders in the film root, format a Harpia contract": kept;
  `item.json` gains the id scheme of `layout/1`.
- fountain-native/io/2 "a sidecar file next to the script": replaced by a
  settings record in the film root, a Harpia message (off hold).
- preprod-link "files in the film root whose format is a Harpia contract":
  kept.

Tasks re-planned: film-bible contract/2, fountain-native io/2, preprod-link
contract/1 (contract/2 needed no change). New epic `layout` (root index and
id scheme; history).
