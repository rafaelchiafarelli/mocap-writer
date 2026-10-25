## 2. Candidate formats

- **Status:** Done (2026-10-25) — comparison below

- **Type:** study (no code)
- **Depends on:** 1 (the list it is scored against)
- **Contract:**
  - In: the confirmed list of task 1; the candidates below (add any)
  - Requires: for each candidate, how it holds each item of task 1, and a
    score on each criterion below, with a reference (spec, program that uses
    it) and its license
  - Delivers: the comparison table, added to this file
- **Pre-work:** —
- **Out of scope:** prototypes
- **Tests:** —

### Candidates (starting points)
1. **Folder bundle** — the film root is the format: `script.fountain` plus
   one small text file (JSON) per item or record, media files next to them.
   Like a macOS package or Scrivener's `.scriv` (a folder of RTF + XML).
2. **Zip container** — one file holding the script, records and media, like
   `.docx`, Fade In's `.fadein` (Open Screenplay Format XML in a zip),
   Highland's `.highland` (Fountain + resources in a zip), Celtx.
3. **SQLite** — one database file (stdlib `sqlite3`, public domain):
   transactions and concurrent readers; media as blobs or as files beside it.
4. **Extended Fountain** — everything in Fountain notes and boneyard blocks;
   one plain-text file.
5. **An existing screenplay format** — Final Draft `.fdx` (XML), Open
   Screenplay Format (Fade In): what they already hold (scene numbers,
   notes, revision marks, tagging/breakdown) and what they cannot.
6. **Hybrid** — Fountain + folder of records (1) + a SQLite index that can
   always be rebuilt from them.
7. **ISOXML-style bundle, Harpia JSON** (Rafael, 2026-10-25) — ISO 11783-10's
   architecture on a folder: `film.json` root index (format version,
   origin, the parts and who owns each); flat records with typed ids
   (`CHR-…`, `SCN-…`, `ANN-…`) linked by id only, with a separate id space
   per writer or agent so records created apart never collide (ISOXML's
   negative ids for terminal-made records); one file per record or per
   scene, so parts are written independently; photos and `.blend` files
   beside the records, referenced like ISOXML's `.BIN` files; every file a
   Harpia message, validated on read. The script stays `script.fountain`,
   its notes pointing to records by id. History is not in ISOXML and needs
   its own design (`history/`).
8. **Change log in SQLite** — every change is a Harpia message appended to
   a log table in `film.db` (WAL mode); the current state is a table
   rebuilt from the log; media in a folder beside it. The log is the
   history; teams sync by exchanging the changes the other has not seen.
9. **CRDT documents** — Automerge or Yjs (MIT): made for live and offline
   team editing, marks on spans of text included; binary.

### Criteria
- holds everything in task 1; the Fountain stays byte-identical;
- readable and diffable as text; easy for an agent to read and to write
  proposals into;
- the writer and an agent at the same time; crash-safe saves;
- large binaries (photos, `.blend`) without slowing down saves;
- copy an item or a whole film; open from Windows;
- history and snapshots (Sync to spec diffs);
- every structured file is a Harpia message, easy to parse and share
  between apps (Rafael, 2026-10-25); Python stdlib or a commercial-use license;
- effort to build and to keep.

### Comparison (2026-10-25)

Candidates 1, 6 and 7 are one family (folder of records) and are scored as
**A**; 3 as **B**; 8 as **C**; 9 as **D**; 2 as **E**. Extended Fountain (4)
cannot hold binaries, states or proposals without burying them in the
script text; existing screenplay formats (5) hold no bible, states or
proposals, and Rafael does not need other screenplay programs (task 1).

| | Big | Team sharing | Debug / readable | History | Effort |
|---|---|---|---|---|---|
| **A. Folder of Harpia JSON records** (ISOXML-style) | thousands of files fine; slower on `/mnt/g` | good: any file sync, small records merge | excellent | to design | low |
| **B. SQLite file** + `media/` | excellent | weak: copies do not merge; unsafe on network shares (sqlite.org) without a sync layer (session extension via `apsw`, cr-sqlite, or a server) | poor without a dump tool | to design | low–medium |
| **C. Change log in SQLite** | excellent | best: exchange unseen changes; per-writer id spaces avoid collisions | good: each change is a message | built in | medium |
| **D. CRDT documents** | good | excellent | poor (binary) | built in | high: young Python bindings, poor Harpia fit |
| **E. Zip container** | poor: every save rewrites the file | easy to send, cannot merge | fair | none | low |

Licenses: stdlib `json`/`sqlite3` (PSF, public domain); `apsw` (zlib-style),
cr-sqlite (MIT/Apache-2.0), Automerge/Yjs (MIT) — all allow commercial use.
