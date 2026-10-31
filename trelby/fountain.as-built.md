# fountain.py — as built

`trelby/fountain.py` (675 lines) makes Fountain 1.1 the writer's own file
format: File → Open reads a `.fountain` into a `Screenplay`, File → Save
writes it back. No wx. The promise is that open → save → open is
byte-identical, and that an edit rewrites only the elements it touched.

## How the round trip works

- `parse(text)` (`trelby/fountain.py:241`) returns a `Source`
  (`trelby/fountain.py:70`): the BOM, the line ending of the first line
  (`eol`, `\n` or `\r\n`), the raw title-page block, a list of `Element`s
  (`trelby/fountain.py:57`) and the `tail` after the last element.
- Each `Element` holds `lt` and `text` (what the editor holds, lines joined
  by `\n`, passed through `util.toInputStr`), `raw` (its exact source, line
  endings included), `pre` (the exact source between the previous element
  and this one) and `decor` (a scene number `#12#` or a dual-dialogue mark
  `^`, with the spaces before it). A scene's number is
  `sceneNum(decor)` (`trelby/fountain.py:151`), and `toLines` puts it on
  the heading's first `Line` as `num` (`trelby/fountain.py:465`;
  fountain-native/scenes/2): the number is never in the editor's text.
- What the editor does not show goes into `pre` (or `tail`): blank lines,
  boneyard blocks that start a line (`/*` up to the line holding `*/`,
  `trelby/fountain.py:273`), synopses `=`, sections `##` and deeper, page
  breaks `===` (`_isHidden`, `trelby/fountain.py:96`).
  `bom + title + Σ(pre + raw) + tail` is the file, character for character.
- `generate(sp)` (`trelby/fountain.py:562`) compares the editor's elements
  now (`elementsOf`, `trelby/fountain.py:441`, `(type, text, num)`, `num`
  the first line's number for a scene, `""` otherwise; empty elements are
  skipped) with `sp.fountainSource.elements`, keyed by `(type, text, num)`,
  upper-cased for types whose export is all caps (`key`,
  `trelby/fountain.py:569`; a changed number makes the element edited), with
  `difflib.SequenceMatcher` (`trelby/fountain.py:654`):
  - **equal** → `pre + raw` (`emitOld`, `trelby/fountain.py:613`); if the
    element was glued to its predecessor (`pre` without a newline) and that
    predecessor is no longer before it, a separator is used instead
    (`sep`, `trelby/fountain.py:607`);
  - **replaced** (edited in place) → the old `pre`, then the element in
    canonical Fountain; same type keeps its `decor` (`emitNew`,
    `trelby/fountain.py:624`), except a scene whose number is not the one
    in it: written as ` #n#`, or nothing without a number
    (`trelby/fountain.py:627-629`);
  - **inserted** → separator + canonical Fountain;
  - **deleted** → the hidden source in its `pre` (if not only blank lines)
    is carried to the next element written (`drop`,
    `trelby/fountain.py:648`).
- The title page is written from its raw block while `titlesKey(sp.titles)`
  equals the one recorded at load (`trelby/fountain.py:582`), else from
  `generateTitle` (`trelby/fountain.py:402`); a blank line is ensured after
  it (`trelby/fountain.py:686`).
- The result is parsed again and compared with what the editor has
  (`trelby/fountain.py:695`). `Result.lost` (`trelby/fountain.py:555`) lists
  the `(type, text)` of elements that will read back differently; the new
  `Source` becomes the script's `fountainSource` once the file is written.

## Element mapping

`classify(lines)` (`trelby/fountain.py:171`) reads one paragraph (lines up
to a blank or hidden line; inside a dialogue block a run of `"  "` lines
followed by more dialogue continues it, `trelby/fountain.py:296`), in this
order:

| Fountain | Element | Written as (`_candidates`, `trelby/fountain.py:504`) |
|---|---|---|
| `!X` | Action, forced | when the natural form reads as something else |
| `# X` | Act break | `# X` |
| `INT.`/`EXT.`/`EST.`/`INT./EXT.`/`INT/EXT`/`EXT/INT`/`I/E` + `.` or space, or `.X` | Scene; `#n#` → `decor`, and `Line.num` | natural, else `.X` |
| a paragraph that is one `[[...]]` | Note | `[[X]]` |
| upper case ending `TO:`, or `>X` not ending `<`, alone | Transition | natural, else `> X` |
| upper-case cue (before any `(`) + more lines, or `@X` | Character; `^` → `decor`; then Paren for `(...)` lines and Dialogue for the rest (empty line = `"  "`) | natural, else `@X` |
| upper case alone, ending in two spaces | Shot | `X  ` |
| anything else (also `>centered<`, inline notes and boneyard) | Action, text as written | — |

`_render` (`trelby/fountain.py:529`) tries the candidates in order and keeps
the first that `classify` reads back as the same element; a first line that
would start a title page is skipped at the top of the file
(`trelby/fountain.py:535`). If none fits it writes the first one and reports
the element as lost (`trelby/fountain.py:550`).

## Title page

The title page is the block of lines at the top, from a `Key: value` line
(`TITLE_KEY_RE`, `trelby/fountain.py:50`; a line in upper case ending in
`:`, such as `FADE IN:`, is not a key, `trelby/fountain.py:106`) to the first
blank line (`trelby/fountain.py:256`). `makeTitles` (`trelby/fountain.py:354`)
builds one title page from it in Trelby's default layout: Title (Helvetica
24 bold, centered, y 105), Author (`by`, ``, names), Contact (left, x 15),
Credit / Source centered from y 150, other keys left from y 220 upwards
(`Key: value`). Emphasis `_*` around values is removed for display. No title
block → no title page.

## Entry points

- `isFountain(fileName)` (`trelby/fountain.py:83`) — `.fountain`, any case.
- `load(text, cfgGl)` (`trelby/fountain.py:483`) → a paginated `Screenplay`
  with default headers and `fountainSource` set, and `sceneNumbersIssued`
  the numbers read (`trelby/fountain.py:492`, fountain-native/scenes/3);
  an empty file gives one empty Scene line (`trelby/fountain.py:476`).
  `OMITTED` headings come back as Scene elements with their number, since
  they are written as `.OMITTED #n#`.
- `generate(sp)` → `Result(text, source, lost)`; the caller writes `text`
  (UTF-8) and stores `source` (`MyCtrl.saveFile`,
  `trelby/trelbyctrl.py:196`).

## Gotchas

- **Per-script settings are not in the Fountain file**: page setup,
  element styles, auto-completion lists, locations, the script's
  spell-checker words and headers stay at their defaults when a `.fountain`
  is opened. Page setup and styles can be kept with Script → Settings →
  Save as / Load. The rest is planned as a record in the film root
  (fountain-native/settings/1, waits for file-format/layout/1).
- **Shot is Trelby's own convention** (upper case + two trailing spaces);
  other Fountain tools, and editors that strip trailing spaces, read it as
  Action. A Shot not in upper case is written as Action and reported lost.
- **Not representable in Fountain**, reported as lost on save: dialogue or a
  parenthetical not under a character, two dialogue elements in a row (they
  join), empty lines inside Action (they split it), dialogue lines with
  leading spaces, a parenthetical that is not one `(...)` line, Note text
  that ends with spaces or holds `]]`.
- Emphasis (`*`, `**`, `_`), inline notes and inline boneyard stay in the
  text as typed characters; the editor shows them as they are.
- Only UTF-8 files open (`MyCtrl.loadFile` shows an error otherwise,
  `trelby/trelbyctrl.py:140`); the BOM and the line ending of the first line
  are kept, and new lines are written with that line ending.
- It is the program's only Fountain reader and writer (fountain-native/io/5):
  Import → Fountain reads through `load` like Open (the tab stays
  untitled), and Export → Fountain and the PDF import command line write
  with `generate`. A screenplay with no `fountainSource` (an import, a new
  script) is written all in canonical form.

## Touchpoints

- Called by: `MyCtrl.readFountain` (Open and Import) / `saveFile` /
  `OnExportScript` (`trelby/trelbyctrl.py:174`, `trelby/trelbyctrl.py:196`,
  `trelby/trelbyctrl.py:1486-1492`); `pdfimport.main`
  (`trelby/pdfimport.py:1151`); `tests/test_fountain.py`,
  `tests/test_pdfimport.py`.
- Uses: `screenplay` constants and `Screenplay`, `titles`, `pml`, `util`,
  `line.Line`; stdlib `difflib`, `re`.
- Read by: the mocap-previz parser reads what this writes.
