# fixtures — sample files the tests load

**Role:** Small input files for `tests/`. All hold the same short upstream
sample script (a night scene at Stonehenge), so imports can be compared
with the native file.
**Entry points:** `tests.u.fixtureFilePath(name)` / `tests.u.load(name)`
(`tests/u.py:31-49`).
**Inputs → Outputs:** read-only test data.

## Files
- `test.trelby` — the reference script, `#Version 2` format (no
  `#Start-Script` line; read with `startSeen = True`,
  `trelby/screenplay.py:286`). Default for `u.load()`.
- `test.txt` — the same script as indented plain text (Trelby's text export
  layout), input of `importTextFile`.
- `test.celtx` — the same script as a Celtx zip (`script-ujq.html` inside),
  input of `importCeltx`.
- `pdf/letter-test.toml` — PDF import profile for the PDFs that
  `tests/test_pdfimport.py` draws (US Letter, Final Draft-like layout:
  right-aligned transitions, margin scene numbers at 72/552, dual-dialogue
  columns).
- `custom-font/Jost-400-Book.ttf` — TrueType font for the custom-font PDF
  test; `custom-font/LICENSE.md` — SIL Open Font License 1.1.

## Key facts / gotchas
- `test.trelby` contains config keys this version no longer has (e.g.
  `Element/Scene/AutoCompletion`), which `Config.load` drops silently.
- The sample is upstream Trelby's, not film material.
- Jost is under the SIL OFL 1.1 (free, commercial use allowed); it is not in
  the license list of the Mocap Studio rule (MIT, Apache-2.0, BSD, CC0,
  CC-BY, GPL family) and is used only as test data.

## Touchpoints
- Read by: `tests/u.py`, `tests/test_myimport.py`, `tests/test_pdfimport.py`,
  `tests/test_renderscreenplay.py`.
