## 1. Story structure study

- **Status:** Done (2026-10-26) — options below; Rafael's choice pending

- **Type:** study (no code)
- **Depends on:** —
- **Contract:**
  - In: structure models; Fountain sections and synopses
  - Requires: for each model, what the writer would show (act bar, beat
    markers, pacing per page) and what it needs in the file; licenses of any
    tool looked at
  - Delivers: options with trade-offs, added to this file, for Rafael to choose
- **Constraints from decisions made elsewhere (2026-10-26):**
  - **The script stays a clean screenplay** (Rafael): no ids, markers or
    structured data in the Fountain text, so it never reads like a
    programming language. Fountain's own sections (`#`) and synopses (`=`)
    are allowed (other tools understand them and they don't print); any
    other structure data lives in records outside the script and is shown
    on demand, as annotations are (fountain-native/notes/1).
  - **Scenes are named by their permanent scene number** (`12`, `12.A`,
    `12.A.1`; fountain-native/scenes/1); a structure record refers to
    scenes by number, never by position or a hidden id.
  - **Records live in the film root** as Harpia JSON records with ids
    `<kind>-<space>-<n>` (file-format/layout/1); a new kind such as `act`
    or `beat` is a change to `film.harpia` in `mocap-contracts`.
- **Pre-work:** —
- **Out of scope:** implementation
- **Tests:** —

### What the writer does today (2026-10-26)
- **Act break** is an element (`@`, `trelby/screenplay.py:25`) that
  **prints**: caps, bold, underlined (`trelby/config.py:495`), like a TV
  `END OF ACT ONE`. Fountain export writes it as centered text `>…<`
  (`trelby/screenplay.py:737`), which reads back as Action, so it does not
  survive a round trip. fountain-native/io/1 already plans act break → `#`.
- **Sections `#` and synopses `=`** are dropped on Fountain import, or
  turned into notes if a checkbox is ticked (`trelby/myimport.py:638-704`).
  The editor has no section element and no depth (`##`, `###`).
- Pages are already counted per scene (`scenereport.py`), so a scene's
  page position is known: pacing needs no new data.

### The models
All four are the same shape: **named spans** (acts, sequences) that
contain each other, plus **named points** (beats), each with a **target
position** as a share of the script's pages. Targets below are for a
110-page script and scale with the real page count.

| Model | Spans | Points | Targets | What the writer would show |
|---|---|---|---|---|
| **Three acts** (Field) | 3 acts | plot points 1 and 2, midpoint | acts 25 / 50 / 25 % | act bar in 3 parts, 3 ticks |
| **Sequences** (Daniel, Gulino) | 3 acts ⊃ 8 sequences | — | ~12–15 pages per sequence | the act bar split in 8 |
| **15 beats** (Snyder, *Save the Cat*) | 3 acts; 6 range beats (Set-up p1–10, Debate p12–25, Fun and Games p30–55, Bad Guys Close In p55–75, Dark Night of the Soul p75–85, Finale p85–110) | 9 point beats (Opening Image p1, Theme Stated p5, Catalyst p12, Break into Two p25, B Story p30, Midpoint p55, All Is Lost p75, Break into Three p85, Final Image p110) | a page for every beat | ticks with target vs actual, "late by 6 pages" |
| **Hero's journey** (Vogler, 12 stages) | 3 acts; 12 stages in order | Ordeal near the middle | loose: order matters, pages don't | the stages in order, no lateness |

What each needs **in the file** is the same for all: which model the film
uses, and for each span or beat **the scene number where it starts**
(scenes/1). A span ends where the next one starts. Nothing else: names,
order and targets come with the model.

What the writer would show, whatever the model:
- **Act bar**: a thin bar along the editor, the script's pages left to
  right, coloured by act (or sequence), a "you are here" mark at the
  cursor, and the model's target lines behind it.
- **Beat ticks** on the bar: the actual page and, ghosted, the target page;
  hover gives the beat, its scene and how many pages early or late.
- **Where am I** in the status area: `Act 2 · Fun and Games · p. 42
  (target 30–55)`.
- **Pacing**: pages per act and per sequence against the target, as a
  report beside the scene report (PDF, like `reports.py`).
- Like annotations, all of it is **off by default** behind a button: the
  editor shows only the script until asked.

### Where the structure is kept
- **S1. All in Fountain sections.** `# ACT ONE`, `## …` for sequences,
  `### Catalyst` for beats, `=` for a line about each. Other Fountain tools
  (Beat, Highland, Better Fountain) show it as an outline and it never
  prints. But the program has to **infer** "depth 3 is a beat, and this one
  is Catalyst" from the text, which the project does not allow; and a
  script with 15 beat headings starts to read like markup.
- **S2. All in records.** A `structure` record in the film root: the model
  and a list `{part: "catalyst", scene: "12"}`. The script is untouched,
  scene moves already rewrite records that name scenes (scenes/1). Other
  tools see nothing.
- **S3. Acts in the script, the rest in records.** Act breaks become
  non-printing `# ACT ONE` sections (what io/1 already plans for the act
  break element); sequences and beats live in the `structure` record by
  scene number. The script keeps one heading per act, which any tool shows;
  the fine structure is declared, not inferred.

A **deleted scene** carrying a beat keeps it on its `OMITTED` heading,
listed to move by hand, as annotations do (notes/1).

### Options for Rafael
- **A. Three acts only, S3.** Act break → `#` section, act bar and where-am-I
  from the sections; no record, no new Harpia kind. Smallest: one task in
  fountain-native (the section element) and one view task. No beats.
- **B. Models as templates, S3** (recommended). The four models above ship
  as **templates** (data: parts, order, targets), not code; a film picks
  one in its `structure` record, and a new model is a new template. Acts
  as `#` sections, beats and sequences by scene number in the record.
  Costs: a `structure` kind (and a `structure-template`) in `film.harpia`
  in `mocap-contracts`, the section element, the record, the bar and the
  pacing report: about five tasks.
- **C. Templates, S2.** As B but the acts are also in the record: the
  cleanest script, but other Fountain tools see no acts, and the writer's
  existing act break element has nowhere to go.

Why B: the four models differ only in data, so building one is building
all; acts stay readable in the script where every tool shows them, while
beats, which change often while writing, stay out of the text.

Later, out of this study: an agent that proposes beats from the script
(a proposal Rafael approves, preprod-link review); TV act structures
(teaser + 4–5 acts with printed act breaks) as more templates.

### Questions for Rafael
1. Which option (A, B, C)?
2. One model per film, or a model plus sequences on top (e.g. 15 beats
   **and** 8 sequences)?
3. Should an act break ever **print** (TV style), or is it always a
   non-printing section in a film script?
4. Show "late by n pages" as a warning, or only as information?

### Tools looked at (ideas only, no code taken)
| Tool | What it does with structure | License |
|---|---|---|
| Beat (macOS) | outline from sections, colours, beat cards | GPL-3.0 |
| Afterwriting | stats: pages per location, page balance | MIT |
| Better Fountain (VS Code) | outline from sections and synopses | MIT (not re-checked) |
| Highland 2, Final Draft (Beat Board, Story Map), Fade In | outline, beat boards | proprietary: ideas only |

The models are ideas and are free to use. *Save the Cat!* is a registered
trademark, so the template is named "15 beats (Snyder)", not after the
book.
