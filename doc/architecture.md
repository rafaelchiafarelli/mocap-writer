# mocap-writer — architecture

The same content as the explainer pages in `doc/architecture/` (open
`doc/architecture/index.html` in a browser; online copy:
https://claude.ai/artifact/KyZacNpzPJsvbTkca2gHAj, private), as plain text
for AI agents: the map, then one section per layer. Read this first, then
the as-built docs (`CLAUDE.md` per folder, `trelby.process.md`,
`trelby/*.as-built.md`), which hold the `file:line` detail this overview
leaves out.

Built from the as-built docs at commit 959bc3c (dev, 2026-10-31), updated
from them after the bug fixes of the same day. When the architecture
changes (a part added or removed, a different flow between parts, a new
record or file format), this file and the pages are rebuilt from the
as-built docs in the same commit, never edited from memory.

## 1. The map (white)

mocap-writer is Trelby, a screenplay editor from 2006, with a film folder
and its records built around it. Read the map left to right: the program
starts, a window holds one editor per script, the editor works on a
screenplay model, and the model is saved as Fountain into a film root that
other Mocap Studio programs read.

Flows (arrow = hands to):

- Launcher → Window
- Window → Editor (keys, commands); Window → Bible panel
- Editor → Screenplay model (commands)
- Screenplay model → Fountain (save / open)
- Fountain → Film root
- Bible panel → Records (edits)
- Film root → Records
- mocap-contracts → Film root (formats)
- Pre-production agents → Film root (reads / proposes)

Parts:

- **Launcher** — starts the program: reads the command line, builds
  `MyApp`, runs the wx main loop. In Mocap Studio it runs inside Docker.
  Files: `trelby.py`, `trelby/trelby.py`, `trelby/opts.py`,
  `docker/run.sh`. Hands the configuration and the files named on the
  command line to the window (`MyApp.OnInit`).
- **Window (MyFrame)** — the menus, the vertical toolbar, the tabs and the
  status area. Every menu item is an `On<Command>` handler, most of them
  forwarding to the current tab's editor. It also keeps the open films and
  shows the bible panel. Files: `trelby/trelbyframe.py`,
  `trelby/trelbypanel.py`, `trelby/misc.py`. Hands key presses and commands
  to the editor of the current tab; the current tab's film to the bible
  panel.
- **Editor (MyCtrl)** — one per tab. Turns keys and clicks into model
  commands, paints the script through a view mode, and loads, saves,
  imports and exports its script. Files: `trelby/trelbyctrl.py`,
  `trelby/viewmode.py`, `trelby/actpanel.py`. Hands commands to the
  Screenplay; the saved text to Fountain; the film's records to the film
  root on save.
- **Screenplay model** — the script as a flat list of `Line`s with the
  cursor, the selection, pagination, every editing command and the undo
  chain. No wx: the tests drive it directly. Files: `trelby/screenplay.py`,
  `trelby/line.py`, `trelby/undo.py`, `trelby/config.py`. Hands its lines
  to the painter, the exporters and Fountain.
- **Fountain** — the native file format. `parse` keeps every element's
  exact source, `load` builds a Screenplay, `generate` writes it back byte
  for byte where nothing changed. Scene numbers are written as `#12.A#`.
  Files: `trelby/fountain.py`, `trelby/scenenumbers.py`. Hands the text of
  `script.fountain` to the disk, and the parsed source back to the model.
- **Film root** — a folder with a `film.json` index: the parts of the
  film, who owns each, the id spaces. Every write goes through it, so
  ownership is checked and the change is logged. Files: `trelby/film.py`,
  `trelby/relink.py`, `trelby/openfilms.py`. Hands the parts' paths to the
  records' modules, and missing files to the relink dialog.
- **Records** — what the script does not hold: the bible (sets,
  characters, props, wardrobe), per-script settings, the front matter,
  annotations, the change log, the scene index and sync files. Files:
  `trelby/bible.py`, `trelby/scriptsettings.py`, `trelby/frontmatter.py`,
  `trelby/annotations.py`, `trelby/sceneindex.py`, `trelby/sync.py`. Hands
  JSON files in the film root, read and written through mocap-contracts.
- **Bible panel** — left of the script: the front matter node, a tree per
  map, the selected item's form generated from the field catalog, the From
  script commands and This scene. Files: `trelby/biblepanel.py`,
  `trelby/bibleform.py`, `trelby/frontmatterform.py`,
  `trelby/biblelinks.py`. Hands the creator's edits to the bible records;
  links between scenes and items.
- **mocap-contracts** — a separate repository, pinned as a git submodule
  at a tag. Its Harpia schema defines every file format; it ships the
  Python classes, the JSON reader and writer and the rules. Files:
  `third_party/mocap-contracts/schema/Include/*.harpia`,
  `mocap_contracts/`. Hands the same formats to the writer and to the
  pre-production agents, so both read the same files.
- **Pre-production agents** — another repository (mocap-preprod). Its
  specialists read the bible, the scene index and the latest change set,
  and write proposals the creator reviews in the writer. Files:
  `bible/scene-index.json`, `bible/sync/*-changes.json`, `bible/`. Hands
  proposals (values in state `proposal`) back to the bible records.

The layers below come in the order a change usually travels: the model,
the editor, Fountain and numbers, the film root, around the code. (The
pages' colours are the order screenplay revision pages go through, white
first.)

Check yourself:

- *Which parts never import wx, and why does that matter?* The model
  (`screenplay`, `line`, `undo`), `fountain`, `scenenumbers`, `film`,
  `bible` and the other record modules. The test suite runs them without a
  display, so everything that matters for the files on disk is tested;
  only dialogs and painting need the real window.
- *Where does the script's text live, and where do its sets and
  characters live?* The text lives in `script.fountain` (the film's
  `script` part). The sets, characters, props and wardrobe live as
  `item.json` folders under `bible/`. The script never holds record data:
  records point to scenes by their permanent number.
- *Why does the writer read its own records through mocap-contracts
  instead of plain JSON?* So the writer and the pre-production agents
  agree on one format, defined once in the Harpia schema: a file that
  breaks the contract is refused on read and never written.

## 2. The model (blue) — a script is a flat list of lines

Trelby keeps no tree of scenes and elements. The script is one Python list
of `Line` objects, already wrapped to the page width. Elements, scenes and
pages are all worked out from that list.

Flows: Line → Element; Element → Commands (edits); Cursor + mark →
Commands; Commands → Undo chain (records); Undo chain → Pagination
(re-paginate).

Parts:

- **Line** — `Line(lb, lt, text, num)`: how the line ends (`lb`), its
  element type (`lt`), its text, and the permanent scene number on a
  heading's first line. File: `trelby/line.py`. Hands its string form
  `lb char + lt char + text` to undo, which stores lines compressed.
- **Element** — a run of lines that ends with a line whose `lb` is
  `LB_LAST`. A paragraph of Action wraps into several lines: all but the
  last end in `LB_SPACE`. File: `trelby/screenplay.py`. Hands its first and
  last index (`getElemFirstIndexFromLine`, `getElemLastIndexFromLine`) to
  every command.
- **Cursor and mark** — `sp.line` and `sp.column` are the cursor;
  `sp.mark` is the other end of a selection. File: `trelby/screenplay.py`.
  Hands the position to commands and to the painter.
- **Commands** — `sp.cmd(name)` calls `<name>Cmd`, then `cmdPost`. A
  command edits the lines, re-wraps the paragraph and records an undo
  step. File: `trelby/screenplay.py`. Hands a `CommandState` back to the
  editor: whether to repaint, re-paginate, or scroll.
- **Undo chain** — a doubly linked list of undo objects: `SinglePara` for
  an edit inside one paragraph, `ManyElems`, `FullCopy` for big changes,
  `SceneNumbers` when numbers change too. File: `trelby/undo.py`. Hands the
  lines before and after an edit, for Undo and Redo.
- **Pagination** — `paginate()` fills `sp.pages` with the last line of
  each page, following the page-break rules (lines of Action and Dialogue
  kept together, `(MORE)`, `CONTINUED`). File: `trelby/screenplay.py`.
  Hands page numbers to the layout view, the PDF and the reports.

The line breaks:

| lb | Value | Means |
|---|---|---|
| `LB_SPACE` | 1 | the paragraph goes on; a space joins this line to the next when the text is exported |
| `LB_SPACE2` | 2 | the same with two spaces (after a sentence) |
| `LB_NONE` | 3 | the paragraph goes on with nothing between (a long word split) |
| `LB_FORCED` | 4 | a line break typed inside the element (Shift+Enter) |
| `LB_LAST` | 5 | the element ends here |

One command traced, typing a character:

1. The editor's `OnKeyChar` gets the key; it is not a keyboard command, so
   it calls `sp.addCharCmd` with a `CommandState`.
2. `addCharCmd` inserts the character at `sp.column` in
   `sp.lines[sp.line].text`, after its typing rules: auto-capitalizing (a
   sentence's start, a lone `i`), `INT.` or `EXT.` turning the element into
   a Scene, `(` turning it into a Paren.
3. The paragraph is re-wrapped (`rewrapPara`), so a word that no longer
   fits moves to the next line and the cursor follows it.
4. The edit is one `SinglePara` undo step: the paragraph's lines before
   and after.
5. Back in the editor: `cmdPost`, re-pagination on a timer, the cursor's
   line scrolled into view, and `updateScreen` repaints.

Exercise. This Fountain is loaded into the default page width:

```
INT. SALA DE JANTAR - NOITE

Ana pega a xícara azul, olha pela janela e sorri para ninguém em particular.
```

How many `Line`s does `sp.lines` hold? Three, checked against the code at
959bc3c:

| # | lb | lt | text | str(line) |
|---|---|---|---|---|
| 0 | LB_LAST | SCENE | INT. SALA DE JANTAR - NOITE | `.\INT. SALA…` |
| 1 | LB_SPACE | ACTION | Ana pega a xícara azul, olha pela janela e sorri para | `>.Ana pega…` |
| 2 | LB_LAST | ACTION | ninguém em particular. | `..ninguém…` |

The blank line between them is not a line: elements are separated by
their spacing setting, not by empty lines. The heading has no number yet
(`num` is empty) until the script is saved.

Check yourself:

- *Why does undo store lines as strings?* `str(line)` is the line-break
  char, the type char, the number between markers and the text: compact,
  and zlib-compressed when shorter, so a long undo chain costs little
  memory. It also carries the scene number, so undo restores numbers.
- *A paragraph of Action becomes longer than the page width. What changes
  in `sp.lines`?* Re-wrapping splits it into more lines: the old last line
  gets `LB_SPACE` (or `LB_NONE` inside a long word) and a new line with
  `LB_LAST` is inserted after it. The element is still one element.
- *Why must `applyCfg` clear the undo chain?* Changing element widths
  re-wraps every paragraph (`reformatAll`), so the stored line lists of old
  undo steps no longer match the script. `reformatAll` even asserts there
  is no undo history.

## 3. The editor (pink) — from a key press to the screen

The wx side: what starts when the program starts, how the window is laid
out, and how one key goes through the editor, the model and the painter.

Flows: Startup → MyFrame → A tab; A tab → Keys and mouse (events); Keys
and mouse → Painting (Refresh); Keys and mouse → updateCommon (after a
command).

Parts:

- **Startup** — `main()` parses the options; `MyApp.OnInit` loads the
  global config and state files, builds the GUI config (fonts, colours),
  makes `MyFrame`, opens the scripts named on the command line, shows the
  splash. Files: `trelby/trelby.py`, `trelby/globaldata.py`,
  `trelby/config.py`. Hands the global data `gd` to every window.
- **MyFrame** — menus, the vertical toolbar, `MyTabCtrl` (the tabs), a
  splitter with the bible panel on the left and the scripts on the right,
  `MyStatus` at the top right (element types, page, zoom). Files:
  `trelby/trelbyframe.py`, `trelby/misc.py`. Hands menu commands to
  `self.panel.ctrl`, the current tab's editor.
- **One tab (MyPanel)** — `MyCtrl` with its vertical scroll bar, a
  horizontal one under it only while the page is wider than the editor
  (the view also follows the cursor sideways), and the act panel at the
  right: one row per act with its scene count. Files:
  `trelby/trelbypanel.py`, `trelby/actpanel.py`. Hands nothing on its own:
  it only lays out the editor and the act panel.
- **Keys and mouse** — `OnKeyChar` looks the key up in the keyboard
  commands (`ConfigGlobal.commands`); a plain character goes to
  `sp.addCharCmd`. A click goes through the view mode's `pos2linecol` to a
  line and column; double and triple clicks are counted by `ClickCounter`.
  Files: `trelby/trelbyctrl.py`, `trelby/clicks.py`, `trelby/util.py`.
  Hands commands to the model.
- **Painting** — `OnPaint` asks the view mode (draft, layout, side by
  side) for the visible `TextString`s and page rectangles, then draws them:
  prop words underlined, the hatch behind scene headings, scene numbers (or
  `(12.A)` for one not given yet), the cursor and selection. Files:
  `trelby/trelbyctrl.py`, `trelby/viewmode.py`, `trelby/propwords.py`.
  Hands pixels to the screen.
- **updateScreen / updateCommon** — after each change: repaint, update the
  status area, the act panel (only if the acts or the cursor's act
  changed) and the bible panel's scene line. File: `trelby/trelbyctrl.py`.
  Hands the cursor's scene to `BiblePanel.showScene`.

One key press traced (the cursor is in an Action line and you press `a`):

1. wx sends `EVT_CHAR` to the focused `MyCtrl`; `OnKeyChar` reads the key
   code (`util.eventKeyCode`).
2. No keyboard command is bound to `a` (other keys go through
   `gd.mainFrame.kbdCommands` to a menu handler or a `cmd<Name>`), so the
   plain character goes to `sp.addCharCmd`.
3. The model inserts it and re-wraps the paragraph (see the model).
4. The editor runs `cmdPost`, re-paginates on a timer, makes the cursor's
   line visible and calls `updateScreen`: the status area shows the
   element type, the act panel and the bible panel's scene line are
   refreshed.
5. `Refresh()` leads to `OnPaint`, which asks the view mode for the
   visible texts and draws them; in Action, a run of capitals you are still
   typing is not underlined until a space or punctuation ends it.

Where the film shows in the window: the bible panel and the Script menu's
film commands (Annotate, Sync to spec on F5, Review proposals) always work
on the current tab's film: `MyFrame.filmOf(ctrl)` finds the open film
whose `script` part is that tab's file. A script that belongs to no film
shows a line saying so in the panel.

Check yourself:

- *Why does the act panel not change size when you zoom?* It draws with
  its own pixel fonts, not the editor's zoomed fonts, and it does not
  scroll.
- *A click lands between two lines in layout view. Who decides which line
  it is?* The active view mode's `pos2linecol`: each mode knows where it
  drew each line. The editor then sets `sp.line` and `sp.column`.
- *Typed text accepts only Latin-1. Does pasted text?* No filter there:
  paste, import and find/replace do not go through `isValidInputChar`, so
  other characters can reach the script. Helvetica and Times measure them
  like `?`.

## 4. Fountain and scene numbers (yellow) — open, change one word, save: only that word changes

Fountain is the writer's own format. The reader keeps the exact source of
every element, so a save rewrites only what you edited. Scene numbers are
permanent: a scene keeps its number when others move around it.

Flows: parse → load → (editor) → generate; scene numbers on the lines go
to `#12.A#` in the text; records follow moved scenes.

Parts:

- **parse** — splits the text into a `Source`: the title page block, then
  elements, each with its exact source (`raw`), the hidden text before it
  (`pre`: blank lines, boneyard, synopses, sections below level 1) and its
  decoration (the `#12#` number, the dual-dialogue mark). A number typed
  before a forced heading by another tool (`.12. INT. ROOM`) is read as
  the scene's number and taken out of the text. File: `trelby/fountain.py`.
  Hands the Source to `load` and, kept on the Screenplay, to `generate`.
- **load** — turns the elements into `Line`s, builds the title pages,
  keeps the Source as `sp.fountainSource` and records the numbers already
  issued. File: `trelby/fountain.py`. Hands a Screenplay to the editor.
- **generate** — walks the script's elements: one whose type and text
  match the source is written from its `raw`; an edited one in canonical
  Fountain, and so is a heading whose number was typed before it, written
  as `INT. ROOM #12#`. The result lists what will not read back the same
  (`lost`). File: `trelby/fountain.py`. Hands the text to
  `MyCtrl.saveFile`, which writes `script.fountain`.
- **Scene numbers** — `Line.num` on a heading's first line. `assign` gives
  numbers by the rule; `prepareSave` numbers new scenes and writes
  `OMITTED` headings for numbers that disappeared; `renumberAll` starts
  again at 1. Files: `trelby/scenenumbers.py`, `trelby/line.py`. Hands the
  numbers to Fountain (`#12.A#`), the screen, the PDF and every record
  that names a scene.
- **Records follow** — a scene found again with exactly its text under
  another number counts as moved: on save its bible links, per-scene
  values, annotations and shot counters are renamed too. Files:
  `trelby/scenenumbers.py`, `trelby/bible.py`, `trelby/annotations.py`.
  Hands `sp.sceneMoves` to `Bible.renameScenes` and
  `Annotations.renameScenes`.

The numbering rule:

- A script with no numbers gets `1, 2, 3…`
- A new scene at the end gets the next whole number.
- A scene inserted between two numbered scenes gets the next sibling of
  the scene before it, if that number is free before the next scene;
  otherwise the first child: levels alternate number and letter, `12`,
  `12.A`, `12.A.1`.
- There is no room between a scene and its own child, before scene `1`,
  or next to a number in another tool's form: the save stops and offers
  Renumber all.
- A number never comes back: a scene deleted after it was numbered leaves
  an `OMITTED` heading on save.
- A heading gets its number as soon as it is finished (it has text and
  the cursor left it); until then the screen shows the number it will
  get, in parentheses.

Exercise. Three scripts, each with one new scene (`?`). What number does
`assign` give it? Checked with `scenenumbers.assign` at 959bc3c:

- `1, 2, ?, 3` → `2.A`: `3` is taken, so the scene becomes the first child
  of `2`.
- `1, 1.A, ?, 2` → `1.B`: the next sibling of `1.A` is still before `2`.
- `1, 2, 3, ?` → `4`: at the end, the next whole number.

Check yourself:

- *You change one word in scene 40 of a script written by another tool.
  Which bytes of the file change?* Only that element's: every other element
  is written from its `raw` source, with its `pre` (blank lines, boneyard,
  notes) in front. That is the byte-identical round trip.
- *Why is a moved and edited scene a new scene?* A move is found by the
  scene's exact text. If the text changed too, nothing proves it is the
  same scene, so its records stay on the old number, now an `OMITTED`
  heading.
- *Where does a film's title page come from when the script is saved?*
  From the film's front matter record: `frontmatter.syncTitle` writes the
  Fountain title block from it before every save of a film's script.

## 5. The film root (green) — a film is a folder of small, checked files

Everything about a film that is not script text lives in JSON files beside
`script.fountain`, each one a mocap-contracts message. The writer owns
most of them; agents get their own space.

Parts:

- **film.json** — the root index: format version, the program that last
  wrote it, the parts (name, path, owner) and the id spaces (code, owner).
  Only a missing or invalid `film.json` stops a film from opening. Files:
  `trelby/film.py`, `schema/Include/film.harpia`. Hands part paths to
  every record module; owners to `checkWrite`.
- **Ids** — a record id is `<kind>-<space>-<n>`, like `prop-w-3`.
  `ids/w.json` holds the writer's counters; `newId` saves the counter
  before it returns the id, so an id is never given twice. File:
  `trelby/film.py`. Hands ids to new bible items and annotations.
- **Bible** — `bible/<map>/<slug>/item.json`, child items nested in their
  parent's folder, photos and plans beside them. Values carry a state
  (`script-stated`, `creator-approved`, `proposal`, `tbd`), a source and
  an author; fields come from the approved catalog. Files:
  `trelby/bible.py`, `trelby/bibleedit.py`,
  `mocap_contracts/catalog/bible-v1.json`. Hands items and their scene
  links to the panel, the scene index and the review view.
- **Change log** — every text write to a part other than the script and
  the history appends a line to `history/<yyyy-mm>.jsonl` with the text
  before and after. Files built from the script (scene index, sync) are
  not logged. Files: `trelby/film.py`, `schema/Include/change.harpia`.
  Hands the history to `revert` and to the review view's reject, which
  puts back the value a proposal replaced.
- **Missing files** — a missing part or file is a `Problem` with a relink
  reference; `RelinkDlg` lets the creator search for it, and a found move
  is offered for the other missing files. A problem with nothing to search
  for (an invalid record, a title page edited elsewhere) is listed as a
  notice with its reason; with only notices the dialog is Film notices,
  without Search or Skip. Files: `trelby/relink.py`, `trelby/relinkdlg.py`.
  Hands new paths back to `film.json` or the item.
- **Other parts** — `settings/script-settings.json` (page setup, styles,
  title layout), `settings/front-matter.json` (title page, overview,
  pitch, argument), `annotations/` (notes anchored by scene and quote),
  `bible/scene-index.json` and `bible/sync/`, `source/` (the original of
  an imported script). Files: `trelby/scriptsettings.py`,
  `trelby/frontmatter.py`, `trelby/annotations.py`, `trelby/sync.py`,
  `trelby/importfilm.py`. Hands their records to the script's tab and to
  the agents.

Why a Harpia contract and not a private format: Mocap Studio's rule is
that applications talk through Harpia: the formats are `.harpia` files in
mocap-contracts, generated into Python (and Java for the camera app), with
the rules `required` cannot express in `mocap_contracts/rules.py`. The
writer and the pre-production agents import the same package at the same
tag, so a field means the same in both, an invalid file is refused on read
by everyone, and changing a format is a reviewed change in one place. A
private JSON written by the writer alone would drift the first time an
agent read it.

Find props traced, from the menu to the files:

1. Bible panel → From script… → Find props calls `OnFindProps`.
2. `biblelinks.propPlan(b, sp)` reads the Action lines of every numbered
   scene: each run of capitalized words (`propwords.find_prop_words`) that
   is not a speaker, not a bible character and not marked "not a prop" is
   a link to a known prop, or a new prop with its scenes.
3. The checklist shows known props ticked and new ones unticked; nothing
   is written until OK.
4. For each new prop, `Bible.create` asks `film.newId("prop")`, which
   writes `ids/w.json` first, picks a free folder slug and writes
   `bible/props/<slug>/item.json`; `Bible.link` adds its scenes.
5. Each write goes through `Film.writeText`: ownership checked, written
   atomically through a temp file, and one line appended to
   `history/2026-10.jsonl`.
6. The props left unticked can be marked "not a prop":
   `bible/not-props.json`, also logged.

Check yourself:

- *An agent writes a proposal. Can it write into `bible/` directly?* Not
  through the writer's checks: `bible/` is owned by the writer. An agent
  gets its own id space and a `proposals-<code>` part (`Film.addSpace`).
  How agents deliver proposals is still an open decision in mocap-preprod.
- *A photo of a set was moved outside the program. What happens on Open
  film?* The item opens; the missing file is a problem with a relink
  reference, listed in `RelinkDlg`, where the creator can search for it. A
  found new location is offered for the other missing files that moved the
  same way.
- *Why are `bible/scene-index.json` and `bible/sync/` left out of the
  change log?* They are built from the script by code and never edited, so
  logging them would only fill the history with copies of the index
  (`Film.derived`).

## 6. Around the code (goldenrod) — what surrounds a change

The program runs and is tested in one Docker image. Every change travels a
fixed branch chain and carries its as-built docs in the same commit. Bugs
are written down and fixed when they get in the way.

Parts:

- **Docker image** — Ubuntu 24.04 pinned by digest; apt installs GTK and
  what the wxPython wheel needs, fonts, evince, the Hunspell pt-BR
  dictionary; Python packages only from a hashed lock
  (`--require-hashes`). The source is mounted, not copied, so code edits
  need no rebuild. Files: `docker/Dockerfile`, `docker/requirements.in`,
  `docker/requirements.lock`, `docker/run.sh`. Hands the same environment
  to the editor (`run.sh`) and to the tests (`test.sh`).
- **Test suite** — pytest over `tests/`, without a display:
  `TRELBY_TESTING` makes the modules import a mock instead of wx. It drives
  the model, Fountain, the film and its records directly. Files: `tests/`,
  `docker/test.sh`, `tests/u.py`. Hands a green suite, which is what "dev
  is not broken" means.
- **What the tests cannot see** — dialogs, painting, the panels' layout.
  Those are checked in the real window: the app is run on the display with
  its dialogs answered by a script, and screenshots are read. Hands a note
  in `tests/CLAUDE.md` saying what was checked by hand, and when.
- **Branch chain** — `dev → features → <initiative> → epics → <epic> →
  tasks → <task>`; commits land on the task branch and every level merges
  up with `--no-ff` once its definition of done holds. Fixes are
  `fixes/<id>/<name>` off `dev`. Files:
  `.claude/skills/mocap-workflow/SKILL.md`, `initiatives/`. Hands finished
  work to `dev`; a release from `dev` to `main` is Rafael's call.
- **As-built docs** — a `CLAUDE.md` per folder, `trelby.process.md` for
  the stages, a `<module>.as-built.md` for large modules. They say what the
  code does, every claim with a `file:line`, and change in the same commit
  as the code. Hands the context a second session needs, and what these
  pages are built from.
- **Bugs** — a bug found is recorded in `initiatives/bugs/` (symptom,
  where, how to reproduce, impact, status), not fixed on the spot. It is
  fixed on a fix branch when it blocks a task or Rafael asks; once pushed,
  its file is deleted. Hands a fix branch, and a gotcha in the as-built
  docs while it is open.

A checklist for reviewing a change:

- Does the commit do what its task file's contract says, and nothing
  outside it?
- Is the task file marked done in the same commit?
- Does the full suite pass in the image (`docker/test.sh`), not only the
  new tests?
- Do the new tests cover the contract's listed tests? For a dialog, does
  `tests/CLAUDE.md` say it was checked in the real window?
- Did every touched folder's `CLAUDE.md` and every changed stage in
  `trelby.process.md` change too? Do the `file:line` references still land
  on what they name?
- If the change touches the architecture, were `doc/architecture.md` and
  the pages in `doc/architecture/` rebuilt from the as-built docs in the
  same commit?
- A new dependency: is it in the hashed lock, is its licence one that
  allows commercial use, and is it written down in `docker/CLAUDE.md`?
- A new file format or field: is it a mocap-contracts change at a new tag,
  never a private format?
- Film material (titles, scenes, characters of a real film) anywhere in
  the repository? It belongs in the film root.

Check yourself:

- *The suite is green but a dialog crashes when opened. How could that
  happen?* The tests import a mock instead of wx, so no dialog is ever
  built in the suite. That is why every dialog change is also checked in
  the real window.
- *You find a bug while working on a task that it does not block. What do
  you do?* Record it as a bug file in its own commit and go on with the
  task; it is fixed on a `fixes/` branch when it gets in the way.
- *Why are hashed locks worth the extra step?* The image installs exactly
  the reviewed files: a package changed upstream under the same version
  would fail the hash instead of slipping in.
