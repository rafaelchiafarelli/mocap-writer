# trelby — the application package: screenplay model, wx editor, import/export, reports

**Role:** All of Trelby's code. One flat package of 74 modules: the
screenplay model (`screenplay`, `line`, `undo`), the native Fountain format
(`fountain`), configuration (`config`,
`mypickle`), the wx editor (`trelbyframe` → `trelbypanel` → `trelbyctrl`,
drawn by `viewmode`), the page language and PDF writer (`pml`, `pdf`), import
(`myimport`), reports and dialogs. Stage-by-stage behaviour is in
`../trelby.process.md`.

**Entry points:**
- `trelby.main()` (`trelby/trelby.py:148`) — the GUI program; called by
  `../trelby.py`.
- `fountain.load(text, cfgGl)` / `fountain.generate(sp)` — the native
  `.fountain` format without any GUI (`tests/test_fountain.py`).
- `screenplay.Screenplay(cfgGl)` and its commands — the model without any
  GUI (what the tests use, through `tests/u.py`).
- `myimport.import*(fileName, frame)` — one function per import format.
- `python -m trelby.pdfimport import|probe ...` — PDF → `.fountain` from
  the command line (`trelby/pdfimport.py:1076`).
- `Screenplay.generate{PDF,RTF,FDX,Html,Text}` — exports; Fountain export
  is `fountain.generate`, the same writer as Save.

**Inputs → Outputs:** `.fountain` scripts, imported `.fdx` / `.celtx` /
`.astx` / `.fountain` / `.fadein` / text files, screenplay PDFs (with a
layout profile), and the config files under
`misc.confPath` → an edited script saved as `.fountain`, exports (PDF, RTF,
FDX, HTML, Fountain, text), report PDFs, and the global config and state
files.

## Files

Model and file format
- `screenplay.py` — `Screenplay`: the script as a flat list of `Line`s, the
  cursor, selection, pagination, every editing command, undo chain and all
  exports; also the `LB_*` and line-type constants;
  `fountainSource` holds the parsed `.fountain` the script came from
  (`trelby/screenplay.py:66`). Detail:
  [screenplay.as-built.md](screenplay.as-built.md).
- `fountain.py` — Fountain 1.1 as the native format, no wx: `parse` keeps
  each element's exact source and the hidden source before it,
  `load` builds a `Screenplay`, `generate` writes unchanged elements from
  their source and edited ones in canonical Fountain (byte-identical round
  trip), and reports what cannot read back the same. Detail:
  [fountain.as-built.md](fountain.as-built.md).
- `line.py` — `Line(lb, lt, text, num)` (`trelby/line.py:16`); `num` is
  the permanent scene number on a heading's first line
  (fountain-native/scenes/2), kept if the line's type changes;
  `str(line)` is line-break char + type char + (`\x01` number `\x01`) +
  text (`trelby/line.py:33`), the form undo stores lines in, so undo keeps
  numbers; `copy()`. `fromStr` has no error checking and is for internal
  storage only (undo).
- `undo.py` — undo objects: `FullCopy`, `SceneNumbers` (a `FullCopy` that
  also restores `sceneNumbersIssued`, `sceneTextsIssued` and `sceneMoves`, `trelby/undo.py:185`), `SinglePara`,
  `ManyElems`, `AnyDifference` (`trelby/undo.py:169-299`); lines are stored as
  zlib-compressed strings when that is shorter (`trelby/undo.py:64`). The
  table at `trelby/undo.py:5-32` says which command uses which.
- `titles.py` — `Titles` (list of title pages) and `TitleString` (lines of
  text at an x/y position in mm, font, style); PML, RTF and the
  `#Title-String` save form (`trelby/titles.py:202`); `sort()` orders each
  page's strings by y, then x (`trelby/titles.py:54`), called by the
  title-page dialog.
- `headers.py` — `Headers` / `HeaderString`: per-page header lines,
  `${PAGE}` replaced by the page number (`trelby/headers.py:90`); default is
  `${PAGE}.` right-aligned on line 1 (`trelby/headers.py:16`).
- `locations.py` — `Locations`: groups of scene headings that are the same
  place, used by the location report; `refresh` drops unknown headings
  (`trelby/locations.py:53`).
- `autocompletion.py` — `AutoCompletion`: per-script completion lists for
  Scene, Character, Transition (13 defaults) and Shot
  (`trelby/autocompletion.py:13-39`).
- `autocompletiontype.py` — `AutoCompletionType`: one element type's
  `enabled` flag and item list.
- `acts.py` — the acts of a script (story-structure/acts/2), no wx:
  `actsOf(sp) -> [Act]` (`trelby/acts.py:35`), one `Act(name, line,
  scenes)` per Act break element, `Act n` when its text is empty, sized
  by the Scene elements up to the next act break; scenes before the first
  act break are an unnamed first part (`name` None), listed only when
  there is an act break; `actAt(acts, line)` → index or None
  (`trelby/acts.py:64`).
- `scenenumbers.py` — permanent scene numbers (fountain-native/scenes), no
  wx: `parse("12.A.1") -> (12, "A", 1)` or None for another tool's form
  (`trelby/scenenumbers.py:32`), `fmt`, `key`; `assign(nums) -> (new,
  noRoom)` gives every scene without a number one by the rule (a fresh
  script `1..n`; at the end the next whole number; else the next sibling
  when the next number is outside the parent, else the first child; no
  room between a scene and its child, before scene `1` or next to another
  tool's form; before a first number above `1`, `1`,
  `trelby/scenenumbers.py:111`); `numberFinished(sp)` gives every
  finished heading (with text, cursor not in it; in a script with no
  number at all, every heading) its number, changing only `Line.num`, no
  undo step (`trelby/scenenumbers.py:317`, fountain-native/scenes/6);
  `scenesOf(sp) -> [(line, num)]` (non-empty headings),
  `report(sp)` (the problems as text, shown on open); `prepareSave(sp)`
  (before a save: `OMITTED` headings for numbers given before and gone,
  numbers for new scenes, one undo step; or the reasons the save must
  wait, `trelby/scenenumbers.py:426`), which also takes a vanished
  number's scene, found again with exactly its text, as moved;
  `renumberAll(sp)` (`trelby/scenenumbers.py:512`); both add the renames
  to `sp.sceneMoves` through `addMoves` (composed, `trelby/scenenumbers.py:224`);
  `sceneTexts(sp)` (`trelby/scenenumbers.py:207`); `labels(sp) -> {line: label}` (the number
  shown for each heading: its number, or the one it will get in
  parentheses, `(12.A)`, or `?` when none fits; the same plan as
  `prepareSave`, `trelby/scenenumbers.py:396`), `labelAt(labs, line)`;
  `clickWarning`, a `ClickWarning` (`trelby/scenenumbers.py:563`): the
  warning on a click on a number, skipped for 5 clicks after "do not show
  this again"; `check(nums) -> [Problem]` (duplicate, order, foreign,
  missing, `trelby/scenenumbers.py:170`).
- `propwords.py` — `find_prop_words(line, typingAt) -> [(start, end,
  run)]` (`trelby/propwords.py:23`): the props of a line, each a run of
  consecutive fully capitalized words (accents included; a hyphen or
  apostrophe joins a word, `trelby/propwords.py:10`) separated by spaces
  only, so punctuation, a digit or a word not fully capitalized ends it; a
  one-letter word sits inside a run but never starts or ends one; with
  `typingAt` (the cursor), a run reaching the end of the line with the
  cursor after it is left out until something ends it (film-bible/links/2,
  rule of 2026-10-25). The editor underlines them in Action lines;
  `biblelinks.propPlan` makes prop records from them. No wx.
- `annotations.py` — the script's annotations (fountain-native/notes/1),
  no wx: records in the film's `annotations/` part, never in the Fountain
  text. `sceneElements(sp)` → per scene number its `Element`s (lines and
  their text joined as Fountain joins them, `trelby/annotations.py:74`);
  `Annotations(film)` loads them (an invalid one is a film problem); `add`
  (a shot gets the next number of its scene from
  `annotations/shot-counters.json`, saved first,
  `trelby/annotations.py:221-270`); `resolve(sp, editing)` → `{id:
  Place(spans, line, attached, why)}` (`trelby/annotations.py:283`): the
  quote in its element, else anywhere in its scene, else (editing) the
  closest text in its element (`difflib`, ratio 0.6); a quote gone moves
  the annotation to its whole element, an element gone (found by its last
  text, or by its index while the scene's element count is unchanged,
  `followElement`, `trelby/annotations.py:374`) to its scene; a scene gone
  leaves it unattached on its number until the save writes the `OMITTED`
  heading; with `editing=False` (just opened) a quote not found is listed
  as unattached instead of moved (`trelby/annotations.py:293-371`); the
  anchors that moved are written by `flush` (`trelby/annotations.py:273`);
  `move` re-attaches, `delete`, `renameScenes` (scenes/5, the shot
  counters too, `trelby/annotations.py:437`), `describe`; `anchorAt(sp)`
  → the anchor of a selection inside one element, else of the cursor's
  whole element (`trelby/annotations.py:491`).
- `annotationdlg.py` — `AnnotationDlg` (`trelby/annotationdlg.py:18`):
  kind (fixed once made), text, and the kind's catalog fields generated
  from `mocap_contracts.annotation` (links by item name; file fields shown,
  not added here); `values()` keeps an unchanged field's state, source and
  author, else `creator-approved`. `AnnotationListDlg`
  (`trelby/annotationdlg.py:216`): Edit / Delete / Attach at the cursor.
- `scriptsettings.py` — a script's settings as the film's
  `settings/script-settings.json` (fountain-native/settings/1), no wx:
  `toRecord(sp, fountainTitle)` → a `mocap_contracts.ScriptSettings` with
  every field (`trelby/scriptsettings.py:114`); `apply(sp, record,
  fountainTitle)` puts it into `sp.cfg`, headers, completion lists,
  locations, the script's words and, while the script's Fountain title
  block is the one the layout was saved with, the title pages; else the
  title page stays as Fountain built it and a problem is returned
  (`trelby/scriptsettings.py:201`); `saveFor(film, sp)` /
  `loadFor(film, sp)` (an invalid record is a film problem and the script
  keeps the defaults, `trelby/scriptsettings.py:318-346`).
- `film.py` — a film root (file-format/layout/1), no wx except the
  version in `_origin` (`trelby/film.py:483`): `Film.open(root, owner)`
  reads `film.json` through `mocap_contracts` and lists what is missing or
  invalid as `Problem(what, where, why)` in `film.problems`
  (`trelby/film.py:79`); only a missing or invalid `film.json` raises
  `FilmError`, naming the path and the broken field. `Film.create(root,
  scriptText)` writes `film.json` with `DEFAULT_PARTS`, the `w` space,
  `ids/w.json` and the folder parts (`trelby/film.py:121`).
  `partOf` / `ownerOf` (prefix by segment, `film.json` → writer,
  `ids/<code>.json` → its space's owner, `trelby/film.py:214-244`);
  `writeText` (atomic, through a temp file) and `deleteFile` refuse with
  `OwnerError` a path this program does not own (`checkWrite`,
  `trelby/film.py:250`). Every `writeText` / `deleteFile` of a text
  record in a part other than the script and the history appends a
  `Change` (time, `by`, path, record id, op, before, after) to
  `history/<yyyy-mm>.jsonl` when this program owns the history
  (file-format/layout/5, `logs` / `log`, `trelby/film.py:306-368`), except
  the files built from the script (`derived`: the bible part's
  `scene-index.json` and `sync/`, `trelby/film.py:320`); an
  unchanged write logs nothing; `changes(by)` reads the log, oldest
  first (`trelby/film.py:371`); `revert(changes, by)` puts records back,
  newest first, and is itself logged (`trelby/film.py:397`).
  `newId(kind, space)` saves the counter before it
  returns the id (`trelby/film.py:415`); `addSpace(code, owner, path)`
  adds an agent's space and its `proposals-<code>` part, checked by the
  contract before anything is written (`trelby/film.py:450`);
  `problemsText(problems)`, the problems as text (`trelby/film.py:474`);
  a missing part's `Problem` carries a `relink.Ref` (`partRef`,
  `trelby/film.py:152`) whose `apply` saves the new path in `film.json`
  (`setPartPath`, `trelby/film.py:173`); `addPart(name, rel)` adds a
  part, checked by the contract, its folder made (`trelby/film.py:187`).
- `sceneindex.py` — the scene index for the mocap-preprod agents
  (preprod-link/contract/1), no wx: `build(sp, b)` → a
  `mocap_contracts.SceneIndex` (`trelby/sceneindex.py:165`): the script's
  sha256 (its Fountain text) and per numbered scene (`biblelinks.scenesWithLines`) its
  number, order, heading parts as written (`headingParts`,
  `trelby/sceneindex.py:30`), the linked set (the one named like the
  location, else the first by name), the speakers (`speaks` on) then the
  bible characters and script speakers named in Action as whole words
  (`speaks` off), the prop words as Find props reads them (no character,
  not "not a prop"), bible ids when known, page and line range (from 1),
  and the sha256 of the scene's text (`sceneText`: one element per line, a
  blank line between, `trelby/sceneindex.py:45`); `write(film, b, sp)`
  into `<bible part>/scene-index.json` by `writer`, not logged
  (`trelby/sceneindex.py:192`).
- `changeset.py` — the change set between two scene indexes
  (preprod-link/contract/2), no wx: `diff(old, new, time)` → a
  `mocap_contracts.ChangeSet` (`trelby/changeset.py:64`), scenes matched
  by number: removed, added, moved (not in the longest run of common
  scenes in the same order, `_kept`, `trelby/changeset.py:31`; old and new
  order), heading changed, text changed (the scene's hash: a heading change
  is also a text change), characters entered / left and props added /
  removed (by bible id, else by the name as compared), set link changed;
  `from_hash` / `to_hash` the indexes' `indexHash` (absent on a first
  sync, `old` None: every scene added).
- `sync.py` — Sync to spec's snapshot and diff (preprod-link/sync/1), no
  wx: `run(film, b, sp)` → a `Run(index, changes, rel)`
  (`trelby/sync.py:48`): the scene index now, its change set against
  `lastIndex` (`<bible part>/sync/last-sync.json`, None before the first
  accept), written to `<bible part>/sync/<yyyymmddThhmmssZ>-changes.json`
  and nothing else; `accept(film, r)` writes the run's index as the
  snapshot and as the agents' `scene-index.json` (`trelby/sync.py:63`);
  `changeText(c, names)` (one change as a panel line, a set's id as its
  name, `trelby/sync.py:84`), `byScene(cs)` (the changes grouped by scene,
  in their order); sync/3: `affected(b, cs)` → `Affected(item, value,
  scene)` for every bible value whose scene (per-scene) or source (the
  scene number that states it) is a scene the sync changed, a move alone
  not counted (`changedScenes`, `trelby/sync.py:124`), never stored and no
  state changed; `affectedText` (`needs review: Ana — Occupation: nurse`).
- `syncdlg.py` — `SyncDlg` (`trelby/syncdlg.py:11`), Sync to spec's
  change panel (preprod-link/sync/2), modeless: a header (first sync /
  `n` changes / nothing changed), a tree with one branch per scene
  (`Scene 12 — INT. SALA`), one line per change and, in bold, the bible
  values that need review there (`sync.affected`); Review… opens
  `ReviewDlg` with the run's changes; a double click goes to
  the scene (`OnGoto`); Accept calls `sync.accept` and turns into
  Accepted; nothing in the bible changes from it.
- `review.py` — the review queue (preprod-link/review/1), no wx:
  `queue(b, changes)` → `Entry(item, value, why)` for every value in
  state proposal or TBD and, with a change set, every value
  `sync.affected` lists (`needs review`), once each, by scene with the
  item-level values last (`trelby/review.py:53`); `latestChanges(film)`
  (the newest `<bible part>/sync/*-changes.json`); `appliesTo` (an
  item-level value's scenes: all of its item's); `approve` (creator-approved,
  source kept; a needs-review value keeps its state), `reject` (the value
  removed and the one it replaced put back, found in the change log by
  `previous`, `trelby/review.py:122`; the contract holds one value per
  field and scene, so a proposal replaces the value), `edit` (the
  creator's text, creator-approved); each item written once per batch,
  put back if the contract refuses it (`_apply`).
- `reviewdlg.py` — `ReviewDlg` (`trelby/reviewdlg.py:15`), modeless: one
  list (scene or `all: 1, 3`, item, field, value, why, source); A
  approves, R rejects (after asking), E or Enter edits, Ctrl+A selects
  all; the approved needs-review lines leave the list for the session.
- `importfilm.py` — an import that ends in a film (import-to-film), no
  wx: `copySource(f, path)` copies the imported file into the film's
  `source/` part, added with `Film.addPart` when the film has none
  (`trelby/importfilm.py:18`); not logged (binary). flow/2: `plan(b, sp)`
  → three `Section(map, links, new)` (sets, characters, props; a name
  made a character is not offered as a prop, `trelby/importfilm.py:48`),
  `Section.lines()` (links first); `apply(b, sections, chosen, notProps,
  linkScenes)` makes the chosen links and new items in one go (without
  `linkScenes`, an import into an open film, new items get no scenes and
  nothing is linked) and marks the new props left unticked "not a prop"
  when asked (`trelby/importfilm.py:63`).
- `biblereviewdlg.py` — `BibleReviewDlg`: the bible review, one
  checklist per map (links ticked; new items ticked when `tickNew`), a
  "not a prop" switch, Create / Cancel; `review(parent, b, sp, tickNew,
  linkScenes, note)` plans, asks and applies, `{}` when there is nothing
  to review, None when cancelled.
- `openfilms.py` — the films open in the window (bugs/editor/20), no wx:
  `OpenFilm(film)` holds the film with its `Bible` and `Annotations`
  (`reload` reads both again, `trelby/openfilms.py:12`); `OpenFilms` keeps
  one per root's real path: `add` (a root opened again replaces its
  entry), `at(root)`, `withScript(fileName)` → the film whose script part
  is that file, or None (`trelby/openfilms.py:44`).
- `bible.py` — the film bible (film-bible/contract/2), no wx: `Bible(film)`
  reads every `bible/<map folder>/<slug>/item.json` (children nested in
  their parent's folder) through `mocap_contracts`; an invalid item, one
  in the wrong map folder, a duplicate id or a parent that does not match
  its folder is a film problem (`load` / `loadFolder`,
  `trelby/bible.py:96-161`); a file value that points at nothing is a
  problem with a `relink.Ref` (`checkFiles`, `trelby/bible.py:164`).
  `Item(msg, folder)`; items by id (`get`), `children(map, parentId)` by
  name; `create` (id from `film.newId`, folder `freeSlug`: the ASCII slug,
  `-2`, `-3` on a clash, never a file folder name inside an item,
  `trelby/bible.py:211-246`); `rename` and `move` move the folder and keep
  the id (`trelby/bible.py:253-296`); `delete` with children; `addFile`
  copies a file into the item's `photos/`, `plans/`... and returns its
  path relative to the item (`trelby/bible.py:309`); `setValues(item,
  field, values, state, source, by, scene, ...)` replaces a field's values
  for a scene key, the department from the catalog, and puts the item back
  if the contract refuses it (`trelby/bible.py:340`); `approve` changes a
  value's state only; `link` / `unlink` scenes (wardrobe: with the
  character); `scenes(item)`; `renameScenes(moves)` (links and per-scene
  values, all at once, by `writer`, `trelby/bible.py:434`); `notProps` and
  `saveNotProps`. Every write
  goes through `Film.writeText`, so ownership is checked and it is logged.
- `bibleedit.py` — what the bible form edits (film-bible/maps), no wx:
  `groups(map)` → `Group`s of catalog `Field`s in catalog order
  (`trelby/bibleedit.py:48`); `text` (a field's values as text: a list
  joined by `; `, a number without its unit, a link as the item's name,
  `trelby/bibleedit.py:67`) and `parse` back (a comma decimal accepted, a
  bad number a `ValueError`, `trelby/bibleedit.py:86`); `commit` stores
  what the creator typed, if it changed, as `creator-approved`, source
  `creator <date>`, by `creator` (`trelby/bibleedit.py:113`); `stateOf`,
  `describe` (the state button's tooltip), `setState` (state, source and
  revisit only; put back if the contract refuses it,
  `trelby/bibleedit.py:165`); `linkChoices` / `setLinks` (keeps the notes
  of the links kept); `addFiles` (into `FILE_FOLDERS[field]`, else `blend/`
  or `files/`) / `removeFile`; `sceneChoices` (the item's scenes and the
  open script's numbers, in script order, `trelby/bibleedit.py:251`);
  `wornScenes`, `wornText` (`Ana in 1, 2`), `setWorn` (a wardrobe item worn
  by a character in exactly these scenes, `trelby/bibleedit.py:283`);
  links/6, scenes by hand for `SCENE_MAPS` (set, character, prop):
  `sceneHeadings(sp)`, `sceneLabels` (`12 — INT. ROOM - DAY`, a scene the
  script no longer has as its number), `linkedScenes(item)` (links without
  a character), `setScenes(b, item, scenes)` (exactly these, one write, put
  back if refused, `trelby/bibleedit.py:329`), `sceneItems(b, scene)`,
  `sceneItemChoices(b)` (children under their parent), `setSceneItems(b,
  scene, ids)` (only the items whose link changes, `trelby/bibleedit.py:381`).
- `bibleform.py` — `BibleForm` (`trelby/bibleform.py:38`): the selected
  item's form under the bible tree, the same for every map, built from
  `bibleedit.groups` (`doBuild`, `trelby/bibleform.py:98`): name, id and
  folder, aliases, scenes; per group a header and per field a label of
  `LABEL_WIDTH`, a control by type (text, multi-line for description and
  notes, combo box with the options for a choice, read-only text with
  Add… for files, also a drop target, and … for links) and a state button
  (`script` / `ok` / `proposal` / `TBD`, its menu approves a proposal or
  sets another state, asking the scene for script-stated and the trigger
  for TBD, `trelby/bibleform.py:336-380`); a per-scene group has a scene
  combo box. A value is saved when its control loses the focus or Enter
  is pressed (`OnCommit`, `trelby/bibleform.py:302`); a wardrobe item has
  a Worn by row: pick a character, tick its scenes (`OnWorn`,
  `trelby/bibleform.py:469`); a set, character or prop has Scenes… by its
  scenes: a checklist linked in one write (`OnScenes`, links/6); the field being typed
  in is saved before another item is shown (`commitFocused`).
- `biblelinks.py` — the script's links to the bible (film-bible/links),
  no wx; each scan returns a plan, applied only with the creator's choice:
  `locationOf(heading)` (no INT./EXT. prefix, no time of day,
  `trelby/biblelinks.py:28`), `norm` (case, accents, spaces ignored),
  `findItem(b, map, name)` (name or alias); `scenesWithLines(sp)` (numbered
  scenes only), `sceneAt(sp, line)`, `itemsInScene(b, scene)`; links/1:
  `setPlan(b, sp)` → links for known locations and `{location: [scenes]}`
  for unknown ones (`trelby/biblelinks.py:109`), `applyLinks`,
  `createSets` (named as the script writes the location); links/2:
  `propPlan(b, sp, cursorLine, cursorCol)` → links for known props and
  `{run: [scenes]}` for runs that are no speaking or bible character, no
  known prop and not marked "not a prop" (`trelby/biblelinks.py:244`),
  compared by `propKey` (no case, accents, or plural `s` on a word),
  `createProps`, `markNotProps`; links/5: `speaker(text)` (a Character
  element's name without extension or `^`), `characterPlan(b, sp)` →
  links for known characters and `{name: [scenes]}` for unknown
  speakers (`trelby/biblelinks.py:175`), `createCharacters`; links/3: `charactersByScene` (the bible
  characters who speak in each numbered scene, `trelby/biblelinks.py:308`),
  `linkWardrobe` / `unlinkWardrobe`, `wardrobeGaps` → `[(scene, character
  id)]` with no wardrobe linked there (`trelby/biblelinks.py:335`);
  links/4: `copyItem(src, item, dst, parent, by, name)` copies an item with
  its file folders and child items into `dst` (the same bible or another
  film's), each with a new id of `dst`'s film, no scene links and no
  per-scene values, and, into another film, no links to other items
  (`trelby/biblelinks.py:360`); `usedIn(b, item)` → its scenes, for the
  warnings (`trelby/biblelinks.py:411`).
- `relink.py` — missing files of a film (file-format/layout/3), no wx:
  `Ref(what, rel, kind, apply)` (`trelby/relink.py:24`); `kindOk` by
  extension (`KINDS`) or folder; `check(root, ref, path)` → the new film
  path, or why not (outside the film root, wrong kind,
  `trelby/relink.py:140`); `pattern(oldRel, newRel)` → the changed prefix
  (`trelby/relink.py:84`), `applyPattern`, `suggest(root, pat, refs)` →
  the refs the pattern finds at an existing path of the right kind
  (`trelby/relink.py:122`).
- `clicks.py` — `ClickCounter` (`trelby/clicks.py:5`), no wx: counts
  mouse presses on the same line within 0.5 s, the double-click event wx
  sends with a second press not counted twice (bugs/editor/14-16).
- `sample.fountain` — sample script (upstream's, converted 2026-10-25),
  loaded by a test-mode hotkey
  (`trelby/trelbyctrl.py:1726`).

Configuration
- `config.py` — `Config` (per script: element widths/indents/spacing and
  styles, paper, PDF options, strings), `ConfigGlobal` (Enter/Tab table,
  keyboard commands, colors, screen fonts, editor behaviour), `ConfigGui`
  (wx objects made from `ConfigGlobal`), line-type/line-break code tables.
  Detail: [config.as-built.md](config.as-built.md).
- `mypickle.py` — `Vars` and the `*Var` classes: typed settings with
  default, min/max and a save name, serialized as `name:value` lines
  (`trelby/mypickle.py:69-85`). Used by every saved object.
- `opts.py` — command-line options: `--test`, `--conf <file>`, script
  names (`trelby/opts.py:5`).
- `globaldata.py` — `GlobalData`: config file paths, MRU list, window
  geometry and view mode (saved to `state`), the three view-mode objects,
  the global spell-checker dictionary (`trelby/globaldata.py:17`).

Application and editor (wx)
- `trelby.py` — `MyApp.OnInit` (startup sequence, `trelby/trelby.py:39`)
  and `main()`; loads translations at import time (`trelby/trelby.py:34`).
- `trelbyframe.py` — `MyFrame`: menus, toolbar, tabs, status area;
  `On<Command>` handlers for every menu item, mostly forwarding to the
  current `MyCtrl`; open/import into a tab; exit, whose Save saves every modified tab and
  stops if one stays unsaved (`saveAll`, `trelby/trelbyframe.py:1584`).
  File → Import (`OnImportScript`: with a film open, into this film, into
  a new folder or just open it) and Import into film… (`OnImportIntoFilm`,
  `importIntoNewFilm`: import, New film, the script saved, the original
  copied into `source/`, `trelby/trelbyframe.py:1201`, then the bible
  review with new items ticked, `reviewImport`, `trelby/trelbyframe.py:1240`;
  into this film: the review over the film's bible, new items without
  scenes);
  File → New film… / Open film… (`OnNewFilm`, `OnOpenFilm`,
  `trelby/trelbyframe.py:746-783`); every open film in `openFilms`, and
  the current tab's film `film` (`showFilm` on a tab switch and on the
  current tab's file change, `filmOf`, `scriptFileChanged`,
  `trelby/trelbyframe.py:716-743`, bugs/editor/20), with
  `filmListeners` (file-format/layout/4, `trelby.process.md` Stage 5), its
  `bible`, and the bible panel in `splitter` with View → Bible
  (`showBible`, film-bible/tree/1, `trelby.process.md` Stage 1); its
  `annotations` and View → Show annotations; Script → Annotate…,
  Annotations here…, Unattached annotations…, Sync to spec… (F5, also a
  toolbar button: the film's script only; an unsaved script is saved
  first, after asking; then `sync.run` and the `SyncDlg`, `OnSyncToSpec`,
  `trelby/trelbyframe.py:867`), Review proposals… (`ReviewDlg` over the
  film's bible and its latest change set, `OnReview`,
  `trelby/trelbyframe.py:908`) (`OnAnnotate`,
  `trelby/trelbyframe.py:922`, `OnAnnotationsHere`,
  `OnAnnotationsUnattached`, `trelby/trelbyframe.py:1035-1063`); on Open
  film the annotations whose text is gone join the film's problems
  (`listUnattached`, `trelby/trelbyframe.py:833`).
  View → Dark theme is a check item kept in step with the theme
  (`updateThemeMenu`, `trelby/trelbyframe.py:1379-1383`, called from
  `MyCtrl.applyGlobalCfg`).
- `trelbypanel.py` — `MyPanel`: one tab = `MyCtrl` + vertical scroll bar
  + `ActPanel` at the right (`trelby/trelbypanel.py:9`); the act panel is
  made before `MyCtrl`, whose constructor already updates it
  (`trelby/trelbypanel.py:28`).
- `biblepanel.py` — `BiblePanel` (`trelby/biblepanel.py:24`): the bible
  panel (film-bible/tree/1) over `MyFrame.bible`, the current tab's film's
  (`setBible`, `trelby/biblepanel.py:113`: on another film's bible the
  field being typed is saved first and nothing stays selected, since ids
  repeat from film to film; with none, a line saying the tab's script is
  not a film's): New / New child /
  Rename / Delete buttons, a `wx.TreeCtrl` with one branch per map
  (`refresh` rebuilds it from `Bible.children`, keeping the selection and
  what was expanded, `trelby/biblepanel.py:134`), a right-click menu
  (`menuItems`, `trelby/biblepanel.py:327`), drag and drop to change an
  item's parent (`OnEndDrag`, `trelby/biblepanel.py:359`); under the tree
  in a splitter, the selected item's `BibleForm` (`makeForm` / `showItem`).
  Errors the film refuses are shown, never raised (`guard`). A line under
  the buttons names the cursor's scene and the bible items linked to it
  (`showScene`, called from `MyCtrl.updateCommon`,
  `trelby/biblepanel.py:490`); This scene… under it, enabled in a numbered
  scene, ticks the sets, characters and props in it (`OnThisScene`,
  links/6). From script… opens the links commands
  (`OnScriptMenu`, `trelby/biblepanel.py:391`): each shows its plan in a
  checklist (`choose`) and does only what is checked; Link scenes to sets
  ticks the links to known sets and leaves new sets unticked
  (`OnLinkSets`, `trelby/biblepanel.py:458`); Find props lists links to
  known props (ticked) and new props (unticked), then offers to mark the
  ones not made as not a prop for the film (`OnFindProps`,
  `trelby/biblepanel.py:552`); Find characters does the same for the
  speakers (`OnFindCharacters`, `trelby/biblepanel.py:694`); Review all… is the bible review of all three (`OnReviewAll`, new items
  unticked); Wardrobe gaps lists the characters in a
  scene with no wardrobe there (`OnWardrobeGaps`,
  `trelby/biblepanel.py:596`). The item menu's Copy makes `<name> copy`
  next to it and names the scenes the original is used in (`OnCopy`,
  `trelby/biblepanel.py:618`); Copy to another film… opens that film's
  bible (the open one, when that film is open in the window) and copies
  into it (`OnCopyToFilm`, `trelby/biblepanel.py:638`).
- `actpanel.py` — `ActPanel` (`trelby/actpanel.py:12`): 200 px (at 96 dpi)
  wide, one row per act with its name, `n scenes` and a bar as long as its
  scene count against the largest act; the cursor's act highlighted; a
  hint when there is no act break. Own pixel fonts, so the zoom never
  changes it, and it does not scroll. `update(sp)` repaints only when the
  acts or the cursor's act changed (`trelby/actpanel.py:40`), called from
  `MyCtrl.updateCommon` (`trelby/trelbyctrl.py:589`); repainted on a theme
  change (`trelby/trelbyctrl.py:638`); `draw(dc, w, h)` does the drawing
  (`trelby/actpanel.py:60`); a click gives the focus back to the script
  (`trelby/actpanel.py:50`).
- `trelbyctrl.py` — `MyCtrl`: the editor widget for one script; key
  handling, mouse, painting, load/save/import/export/print, dialogs and
  reports for its script. Detail: [trelbyctrl.as-built.md](trelbyctrl.as-built.md).
- `viewmode.py` — the three screen layouts (draft, layout, side by side):
  where each line is drawn and which line/column a mouse position hits.
  Detail: [viewmode.as-built.md](viewmode.as-built.md).
- `ids.py` — wx menu ids (`ID_FILE_NEW_FILM`, `ID_FILE_OPEN_FILM`,
  `ID_VIEW_BIBLE`, `ID_VIEW_ANNOTATIONS`, `ID_SCRIPT_ANNOTATE...`,
  `ID_SCRIPT_SYNC`, `ID_SCRIPT_REVIEW` for the film) and `idToLTMap` (right-click "Element type" ids →
  line types, `trelby/ids.py:93`).
- `misc.py` — platform flags, `progPath` / `confPath` (`misc.init`,
  `trelby/misc.py:23`), `version` (`trelby/misc.py:20`), and shared widgets:
  `MyTabCtrl` (tab bar, `trelby/misc.py:287`), `MyStatus` (status area
  with the zoom control, `trelby/misc.py:156`), `MyFSButton`, `CheckBoxDlg`
  (`trelby/misc.py:761`), `ScriptChooserDlg`, `TextDlg`, `TextInputDlg`,
  `KeyDlg`, `MRUFiles` (`trelby/misc.py:1064`).
- `gutil.py` — GUI helpers: listbox select/add, stock buttons,
  `showTempPDF` (temp file + viewer, `trelby/gutil.py:82`).
- `util.py` — text and number helpers, the text-measuring DC,
  `eventKeyCode` (key code of a char event, `trelby/util.py:209`), `Key`
  (keyboard shortcut ↔ int, `trelby/util.py:820`), file load/write
  (`trelby/util.py:999-1091`), PDF viewer lookup and launch
  (`trelby/util.py:1206-1269`).
- `error.py` — `TrelbyError`, `ConfigError`, `MiscError`.
- `translations.py` — `trelby_translations_load()`: picks the gettext
  catalog in `locales/` from `$LANG` and installs `_` as a builtin
  (`trelby/translations.py:10`).
- `splash.py` — `SplashWindow`: logo, version, random quote from
  `resources/quotes.txt`; closes on click or after `splashTime` seconds
  (`trelby/splash.py:61-64`); also the About box (`delay = -1`).

Page language and PDF
- `pml.py` — PML ("Page Modeling Language"): `Document` → `Page` → draw ops
  `TextOp`, `LineOp`, `RectOp`, `QuarterCircleOp`, `PDFOp`; all positions in
  mm from the top-left (`trelby/pml.py:38-245`). `TextFormatter` lays out
  plain report text into pages (`trelby/pml.py:250`).
- `pdf.py` — `generate(doc)`: draws a PML document with ReportLab, one
  `PDF*Op` per PML op, custom TrueType fonts, TOC outline. Detail:
  [pdf.as-built.md](pdf.as-built.md).
- `mypager.py` — `Pager`: the PML document being built plus scene state
  shared across `generatePMLPage` calls (`trelby/mypager.py:6`): `scene`,
  the current scene's number label, `sceneLabels`
  (`scenenumbers.labels`, filled when first needed), `sceneContNr`.
- `fontinfo.py` — PDF core-font metrics: Courier (fixed 600 units), and
  256-entry width tables for Helvetica and Times (`getMetrics`,
  `trelby/fontinfo.py:11`).
- `truetype.py` — minimal TrueType/OpenType parser: PostScript name and
  embedding permission, used to validate custom PDF fonts
  (`trelby/configpages/pdffontspanel.py:156`).

Import
- `myimport.py` — importers for Adobe Story, Fade In, Celtx, Final Draft,
  indented plain text, and the GUI side of PDF import (a `.fountain` is
  imported through `fountain.load`, `MyCtrl.importFile`)
  (`importPdf`: import report window, error box, trace). Detail:
  [myimport.as-built.md](myimport.as-built.md).
- `pdfimport.py` — PDF import without wx: pdfplumber text lines →
  elements by position, the layout detected from the PDF (or a profile);
  doubtful spots become `IMPORT:` notes; `probe`, report, trace, and the
  `python -m trelby.pdfimport` CLI. Detail:
  [pdfimport.as-built.md](pdfimport.as-built.md).
- `importdlg.py` — `ImportDlg`: lets the user set the element type of each
  indentation level found in a text file (`trelby/importdlg.py:8`).
- `indent.py` — `Indent`: statistics for one indentation level of a text
  file (`trelby/indent.py:2`).

Reports
- `reports.py` — `gen{Scene,Location,Character,Script}Report`: option
  dialog, build, show PDF (`trelby/reports.py:12-98`).
- `scriptreport.py` — `ScriptReport`: line counts per type, interior /
  exterior share, scene and action lengths, speaking characters.
- `scenereport.py` — `SceneReport` / `SceneInfo`: one entry per scene
  (number label from `scenenumbers.labels`, heading, lines, pages,
  speakers).
- `locationreport.py` — `LocationReport`: scenes merged by `Locations`.
- `characterreport.py` — `CharacterReport` / `CharInfo`: speeches, lines,
  words, pages and scenes per speaking character.
- `dialoguechart.py` — `genDialogueChart` + `DialogueChart`: per-page bars of
  who speaks, with sort options (`trelby/dialoguechart.py:14`).
- `pagelist.py` — `PageList`: page numbers formatted as `1-3, 7`
  (`trelby/pagelist.py:6`).

Dialogs
- `relinkdlg.py` — `RelinkDlg` (`trelby/relinkdlg.py:14`): the one
  warning for a film's problems on open; per missing file Search… (a file
  or folder dialog, `askPath`) or Skip; a found file is applied at once and
  its pattern's finds are offered in a `wx.MultiChoiceDialog`, all checked,
  and applied only when accepted (`OnSearch`, `trelby/relinkdlg.py:134`);
  an invalid file shows its reason and can't be searched for.
- `cfgdlg.py` — `CfgDlg`: settings dialog; global pages or script pages
  from `configpages/` (`trelby/cfgdlg.py:21`).
- `finddlg.py` — `FindDlg`: find and replace, optional element-type filter;
  replace is one undo step per hit (`trelby/finddlg.py:403`).
- `spellcheck.py` — the dictionary languages `LANGUAGES` (`en`:
  `dict_en.dat`; `pt-BR`: Hunspell `pt_BR` through `pyenchant`,
  spellcheck/pt-br/1, `trelby/spellcheck.py:7`); word list `dict_en.dat`
  (`loadDict`), `loadLanguage(lang)` → None or the message naming the
  missing dictionary and how to get it (`trelby/spellcheck.py:64`),
  `suggest(lang, word, dicts)` (up to 5: Hunspell's, after the user's words
  within edit distance 2, or the closest `dict_en.dat` words then the
  user's, `trelby/spellcheck.py:97`), user dictionaries (`Dict`),
  `SpellChecker(sp, gScDict, lang)` (walks the script word by word; a word
  is known in the language's dictionary, as written or lower-cased, in
  `SCRIPT_WORDS` (`int`, `ext`, `est`), in character names, the script's
  or the global dictionary, or is a number), `lev` (edit distance).
- `spellcheckdlg.py` — `SpellCheckDlg`: replace / skip / add to script or
  global dictionary / suggest (`spellcheck.suggest` in the setting's
  language, the case of the word kept).
- `spellcheckcfgdlg.py` — `SCDictDlg`: edit a dictionary's word list.
- `namesdlg.py` — `NamesDlg`: character name database from `names.txt`
  (`readNames`, `trelby/namesdlg.py:14`), filter by type, sex and text,
  insert into the script.
- `namearray.py` — `NameArray`: compact storage for ~205 000 names with
  type and sex (`trelby/namearray.py:5`).
- `charmapdlg.py` — `CharMapDlg`: grid of the Latin-1 characters, inserts
  the selected one (`trelby/charmapdlg.py:25`).
- `titlesdlg.py` — `TitlesDlg`: edit title pages, with `TitlesPreview`.
- `titlespreview.py` — `TitlesPreview`: draws a title page scaled to the
  widget (`trelby/titlespreview.py:6`).
- `headersdlg.py` — `HeadersDlg`: edit page headers, PDF preview.
- `locationsdlg.py` — `LocationsDlg`: group scene headings into locations.
- `autocompletiondlg.py` — `AutoCompletionDlg`: edit completion lists.
- `manual.py` — Help → Manual (`MyFrame.OnHelpManual`): `build(prebuilt,
  docDir)` returns the prebuilt `manual.html` or makes it from
  `doc/manual.xml` with lxml and the DocBook XSL stylesheets, else raises
  `ManualError` (`trelby/manual.py:27-50`); `ManualFrame` shows it in a
  `wx.html.HtmlWindow`, `#` links scroll inside it.
- `commandsdlg.py` — `CommandsDlg`: HTML list of commands and their keys,
  can be saved to a file.
- `watermarkdlg.py` — `WatermarkDlg`: one watermarked PDF per line of text
  (`trelby/watermarkdlg.py:12`); an unusable custom PDF font
  stops it with a message.

Data and folders
- `dict_en.dat` — English word list for the spell checker, one word per
  line (175 365 lines).
- `names.txt` — name database: `N<type>` lines start a group, `M<name>` /
  `F<name>` lines add names (204 761 lines).
- `__init__.py` — empty.
- `pdfprofiles/` — optional TOML layout profiles for the PDF importer's
  command line, and the profile format (its own `CLAUDE.md`).
- `configpages/` — the settings-dialog pages (its own `CLAUDE.md`).
- `resources/` — icons, toolbar SVGs, splash logo, quotes (its own
  `CLAUDE.md`).
- `locales/` — compiled gettext catalogs `en` and `it` (its own `CLAUDE.md`).

## Key facts / gotchas
- **A `.fountain` keeps no per-script settings** (page setup, element
  styles, auto-completion, locations, script dictionary, headers, title
  layout): a script opened on its own opens with defaults. A film's script
  keeps them in the film's settings record (`scriptsettings`,
  fountain-native/settings/1): saved with the script, applied when Open
  film opens it. Shot is written as upper case + two trailing spaces,
  Trelby's own convention (`trelby/fountain.py:504`).
- **`_` is a builtin installed by `translations.trelby_translations_load()`**
  (`trelby/translations.py:26`); no module imports it. The tests get it
  from `tests/u.py:16`.
- **Messages are translated, then formatted:** `_("…{}").format(x)`; a
  translated string is never an attribute or save name: helpers that build
  attribute names take a fixed key and a separate label
  (`tests/test_i18n.py` checks both). English is the only GUI language
  Mocap Studio needs (Rafael, 2026-10-27): the inherited `it` catalog is
  not kept in step, so a changed message is simply untranslated there.
- **`TRELBY_TESTING` env var** makes `config`, `misc`, `util` and `gutil`
  import a `Mock` instead of `wx` (`trelby/config.py:14-19`) and leaves
  `ConfigGlobal.commands` empty (`trelby/config.py:742-745`).
- **Text input is Latin-1 only when typed**: `util.isValidInputChar`
  accepts codes 32–255 (`trelby/util.py:219`), but paste, import and
  find/replace do not filter (`util.toInputStr` only removes form feeds and
  turns tabs into `|`, `trelby/util.py:233`). The `toUTF8` / `fromUTF8` /
  `cleanInput` helpers are identity functions left from the Python 2 code
  (`trelby/util.py:194-245`). Helvetica and Times measure a character
  above U+00FF like `?` (`trelby/fontinfo.py:50-65`); Courier has no table.
- `misc.progPath` is the repository root (parent of `trelby/`,
  `trelby/misc.py:54`), so resources are addressed as
  `trelby/resources/...` (`trelby/splash.py:39`).
- `trelby/manual.html`, `dict_en.dat.gz`, `names.txt.gz` and `trelby.1.gz`
  are build products of `../Makefile`, not in git; without
  `manual.html`, Help → Manual makes the page from `doc/manual.xml`
  (`manual.py`).
- Toolbar tooltips open partly off-screen (Rafael's review of unmodified
  Trelby, 2026-10-23); the toolbar is vertical (`trelby/trelbyframe.py:242`)
  and its tooltips come from `shortHelp` (`trelby/trelbyframe.py:258-263`). Bug: [bugs/editor/3](../initiatives/bugs/epics/editor/tasks/3-tooltips-off-screen.md).
- Most source files are UTF-8 even where the header says `iso-8859-1`
  (e.g. `trelby/trelbyctrl.py:1`).
- A missing file part other than the script (the settings record) is not
  a problem on open: it was not written yet (`trelby/film.py:85-89`).
  Missing folder parts, the script and the writer's `ids/w.json` are; with
  `ids/w.json` lost, `newId` refuses rather than start again at 1.
- A bible item's rename or move is logged as its old `item.json` deleted
  and the new one created; the files that moved with the folder are not
  logged, so a revert puts the `item.json` back but not the files
  (`Bible.moveFolder`, `trelby/bible.py:283`).
- `BibleForm` is rebuilt without `Freeze()`: GTK aborts
  (`gtk_text_btree_find_line_top`) when multi-line text controls are made
  in a frozen window (found 2026-10-28). While it rebuilds, `building`
  stops the destroyed controls' focus-loss from saving into the next item
  (`trelby/bibleform.py:90-96`).
- A link's note (e.g. the kind of a relationship) is kept and shown in the
  state button's tooltip, but the form has no control to type one.
- The editor underlines every run of capitals, character names and "not a
  prop" words included: the underline knows nothing of the bible; Find
  props skips them.
- A move is found by the scene's exact text: a scene edited as well as
  moved is a new scene, and its records stay on the old number (now an
  `OMITTED` heading). Renumber all removes the `OMITTED` headings, and
  records still naming those numbers keep them (fountain-native/scenes/5).
- Annotation anchors follow the text only when the script is placed:
  every paint while annotations are shown, and every save of the film's
  script. Edits made with annotations hidden are caught up at the save,
  from the last text each anchor saw.
- The change log holds text only: `film.json`, the id counters, the
  script (saved by `MyCtrl.saveFile`, not through `Film`) and binary files
  are not logged; an agent's own writes are not logged either (it does
  not own `history/`).

## Touchpoints
- Called by: `../trelby.py`; `../tests/` (through `tests/u.py`).
- Depends on: wxPython 4 (GUI), lxml (HTML/FDX export, XML imports),
  ReportLab (PDF), pdfplumber (PDF import), `mocap_contracts` (film
  root formats, `../third_party/mocap-contracts`, with protobuf), stdlib `tomllib` (profiles,
  Python ≥ 3.11), stdlib `gettext`, `zipfile`, `zlib`, `difflib`.
  Versions: `../docker/requirements.lock`.
