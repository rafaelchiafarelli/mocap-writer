## 1. What the format must hold

- **Status:** Done (2026-10-25) — confirmed through Rafael's answers below

- **Type:** study (no code); Rafael confirms, cuts or extends the list
- **Depends on:** —
- **Contract:**
  - In: the decisions so far (listed below with their source)
  - Requires: every item says what it is, who writes it, who reads it, how
    big it gets, and how often it changes
  - Delivers: the confirmed list below, with the date
- **Pre-work:** —
- **Out of scope:** choosing a format (task 2, 3)
- **Tests:** —

### Pre-filled list (to confirm)

**The script**
- Fountain 1.1 text, open → save → open byte-identical, readable by other
  Fountain tools and by the mocap-previz parser (fountain-native/io/1).
- Scene numbers: permanent, `12A` for inserts, not editable, written as
  `#12A#` (fountain-native/scenes/1, 2026-10-25; the notation became
  `12.A`, nested `12.A.1`, on 2026-10-26).
- Notes on spans of text (fountain-native/notes/1; kept outside the script text, decided 2026-10-26).
- Title page.
- Acts and beats: where a scene is in the story (story-structure, study).

**Scene annotations** (Rafael, 2026-10-25; fields in film-bible
contract/1, "Scene annotations")
- On Action (notes; character, prop, set, sound and general directions;
  special effects), Transition (type, duration, sound bridge...) and Shot
  (size, angle, lens, movement, machinery, frame rate, previz camera...).
- Anchored to an element or a span of its text; kind, text, links to bible
  items, state and source, like every value.
- Rafael's idea: mark them with Fountain notes. Open: the whole annotation
  in the note (one file, but structured fields, states and agent proposals
  then live inside the script text, and other Fountain tools show them
  inline), or a short typed note in the text pointing to a record kept
  elsewhere (the script stays readable; a note can be orphaned).
  Decided 2026-10-26: neither; the records hold their own anchor and
  nothing goes in the script text (fountain-native/notes/1).
- Could be many: tens per scene, thousands per film.

**Per-script settings** (were in `.trelby`)
- Page setup and element styles (also savable today with Script →
  Settings → Save as), auto-completion lists, locations (heading groups),
  the script's spell-checker words, page headers.

**The film bible** (film-bible)
- Maps: sets, characters, props, wardrobe; each item can hold child items
  (a tree, like Windows Explorer).
- Each item: fields from an approved catalog (contract/1); every value has a
  **state** (`script-stated`, `creator-approved`, `proposal`, `TBD`) and a
  source (scene or decision).
- Files per item: photos, floor plans, `.blend` files — large binaries.
- Stable ids, independent of names and folder names.
- Copy an item inside a film or to another film, linked or not.

**Links**
- Scene ↔ set; prop runs in Action ↔ props (a run of capitalized words,
  film-bible links/2); wardrobe ↔ character × scene; notes ↔ text spans.
- Everything outside the script points to the scene number (the scene's identity, 2026-10-25), never
  to a position.

**Pre-production link** (preprod-link)
- Scene index: number, order, heading parts, linked set, characters, props,
  page and line range, a hash of the scene's text.
- Snapshots and the change set between two Sync to spec runs.
- Agent proposals and their review: approved / rejected, in batches; a
  decision is never reopened while its source did not change; a value
  decided on an item applies to every scene unless a scene overrides it.

**Who reads and writes it**
- The writer (Python, wx) — reads and writes everything.
- mocap-preprod agents (hosted Claude) — read; write only proposals.
- mocap-previz — reads the script and the index.
- mocap-dashboard — reads state.
- Rafael — opens files from Windows (`G:`), copies films around.

**Constraints already in force** (`mocap-workflow`)
- Python is the work language; licenses must allow commercial use;
  messages between apps are Harpia contracts (`mocap-contracts`); large
  binaries stay out of git; nothing film-specific in a repository; a film
  lives in its **film root**.

### Answers (Rafael, 2026-10-25)
- **A film root is not a git repository:** it is a folder, and everything
  about the film is in it. → History and snapshots (Sync to spec diffs,
  undoing a bad agent pass) must come from the format itself, not from git.
- **The writer and an agent can write the same film at the same time, but
  not the same file:** they work on separate parts of the pipeline. → The
  format must split into parts that are written independently (no single
  file everyone rewrites); a part needs one clear owner at a time.
- **One file or a folder: not decided.** Online work will come: the film is
  a team effort in the future, not one person's. → Prefer a design that can
  later be shared or synced between people (small independent records,
  stable ids, changes that merge), over one that only works on one disk.
- **Other screenplay programs: don't care.** Fountain compatibility is kept
  for its shareable nature while it is cheap; it may be dropped if the
  format needs it. It is an initial step. → Byte-identical Fountain is a
  strong preference, no longer a hard requirement; a Fountain export would
  be enough.
- **ISOXML philosophy** (Rafael has worked with ISO 11783-10 and finds it
  easy to debug, a good source of truth). → The design follows it: one root
  index file with format version and origin; flat records with typed,
  stable ids, linked by id only; records split into separate files, one
  owner each; large binaries beside the records, referenced, never
  embedded; strict validation on read that names the broken field. Not its
  syntax: readable names, not 3-letter tags.
- **Easily parseable and shareable via Harpia.** → Every structured file is
  a Harpia message (`mocap-contracts`, JSON through `to_json`/`from_json`),
  so any app reads it with the generated classes and a broken file fails
  with the path of the problem. XML would need a second schema system next
  to Harpia (weighed in task 2; Rafael chose option A in task 3).
