# pdfprofiles — layout profiles for the PDF importer

**Role:** Optional TOML layout profiles: one file per PDF layout that
`trelby/pdfimport.py` uses instead of detecting the layout from the PDF.
Since 2026-10-24 (Rafael) File → Import detects the layout and asks nothing;
a profile is only for the command line (`--profile`), for a PDF the
detection reads wrongly, and for tests.
**Entry points:** `pdfimport.loadProfile(path)` (`trelby/pdfimport.py:167`).
**Inputs → Outputs:** `python -m trelby.pdfimport probe <pdf>` output (the
indents and the detected layout) → a hand-written profile → `.fountain`.

## Files
- `trelby-a4.toml` — Trelby's own PDF export with the default script
  settings (A4, Courier 12): scene/action 108, dialogue 180, parenthetical
  223.2, character 266.4, transition 432; drops page numbers, `CONTINUED:`,
  `(CONTINUED)`, `(MORE)`. Built with `probe` on an export of
  `tests/fixtures/test.trelby` (now `test.fountain`).

## Profile format

Positions are PDF points (1/72 in) from the **top left** of the page, as
`probe` prints them. Keys (any other key is an error,
`trelby/pdfimport.py:179-193`):

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
| `[scene_numbers]` | — | `left` / `right` x of margin scene numbers, `pattern` (default `^\d+[A-Z]*\.?$`), `tolerance`; `inline`: regex for a number written at the start of the heading, group 1 = the number (e.g. `'^(\d+[A-Z]*)\.\s+'` for `12. INT. …`) |
| `[dual]` | — | `left` / `right`: lists of rules (as `[[indent]]`) for the two dual-dialogue columns |

Elements: `scene`, `action`, `character`, `parenthetical`, `dialogue`,
`transition`, and `scene_action` (scene if the line starts with a
`scene_prefixes` entry, or with an `inline` scene number followed by one;
action otherwise). Prefixes are compared upper-cased and literally, so
`"INT "` (with the space) catches headings typed without the dot.

## Key facts / gotchas
- **TOML table scoping:** a top-level key written after a `[[indent]]`,
  `[[drop]]` or `[dual]` header belongs to that table. Put the top-level
  keys first; the parser rejects the misplaced key with its table's name
  (`trelby/pdfimport.py:190-193`).
- Regexes in basic strings (`"..."`) need doubled backslashes; literal
  strings (`'...'`) do not.
- No per-program profiles: the planned Final Draft / Celtx / Word / Google
  Docs profiles were dropped when the layout became detected (pdf-import
  initiative, task importer/1, now in git history).

## Touchpoints
- Read by: `trelby/pdfimport.py` (CLI `--profile`),
  `tests/test_pdfimport.py` (every profile here must parse).
