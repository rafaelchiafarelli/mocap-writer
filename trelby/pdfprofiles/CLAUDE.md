# pdfprofiles — layout profiles for the PDF importer

**Role:** One TOML file per PDF layout (source program + paper + settings)
that `trelby/pdfimport.py` uses to classify each line of a screenplay PDF by
its position. A profile is always chosen explicitly (File → Import asks for
it, the CLI takes `--profile`); the importer never guesses one.
**Entry points:** `pdfimport.loadProfile(path)` (`trelby/pdfimport.py:114`);
the File → Import profile dialog opens in this folder
(`trelby/myimport.py:768`).
**Inputs → Outputs:** `python -m trelby.pdfimport probe <pdf>` output →
a hand-written profile → `.fountain` / editor lines.

## Files
- `trelby-a4.toml` — Trelby's own PDF export with the default script
  settings (A4, Courier 12): scene/action 108, dialogue 180, parenthetical
  223.2, character 266.4, transition 432; drops page numbers, `CONTINUED:`,
  `(CONTINUED)`, `(MORE)`. Built with `probe` on an export of
  `tests/fixtures/test.trelby`.

## Profile format

Positions are PDF points (1/72 in) from the **top left** of the page, as
`probe` prints them. Keys (any other key is an error,
`trelby/pdfimport.py:126-140`):

| key | default | meaning |
|---|---|---|
| `name` | file name | shown in error messages |
| `description` | — | free text |
| `tolerance` | 3.0 | ± points around each rule's position |
| `segment_gap` | 28.0 | a horizontal gap wider than this splits a line into columns (dual dialogue, margin text) |
| `paragraph_gap` | 18.0 | a vertical step between line tops larger than this ends an element |
| `skip_pages` | 0 | leading pages ignored (title page); the CLI's `--skip-pages` overrides |
| `scene_prefixes` | `[]` | used by `scene_action` rules: a line starting with one is a scene heading |
| `character_suffix` | `[]` | regexes cut from the end of character names, e.g. `(CONT'D)` |
| `[[indent]]` | required | `element` + exactly one of `x` (left edge), `x1` (right edge, for right-aligned transitions), `xc` (center); optional own `tolerance`. First match wins |
| `[[drop]]` | — | page furniture: `pattern` (regex on the whole line), optional `top_min` / `top_max` |
| `[scene_numbers]` | — | `left` / `right` x of margin scene numbers, `pattern` (default `^\d+[A-Z]*\.?$`), `tolerance` |
| `[dual]` | — | `left` / `right`: lists of rules (as `[[indent]]`) for the two dual-dialogue columns |

Elements: `scene`, `action`, `character`, `parenthetical`, `dialogue`,
`transition`, and `scene_action` (scene if the line starts with a
`scene_prefixes` entry, action otherwise).

## Key facts / gotchas
- **TOML table scoping:** a top-level key written after a `[[indent]]`,
  `[[drop]]` or `[dual]` header belongs to that table. Put the top-level
  keys first; the parser rejects the misplaced key with its table's name
  (`trelby/pdfimport.py:137-140`).
- Regexes in basic strings (`"..."`) need doubled backslashes; literal
  strings (`'...'`) do not.
- Starter profiles for Final Draft, Celtx, Word and Google Docs are not here
  yet: they are built from real PDFs (see the task file
  `initiatives/pdf-import/epics/importer/tasks/1-pdf-importer.md`).

## Touchpoints
- Read by: `trelby/pdfimport.py`, `trelby/myimport.py` (`importPdf`),
  `tests/test_pdfimport.py` (every profile here must parse).
- Packaged through `setup.cfg` (`pdfprofiles/*`).
