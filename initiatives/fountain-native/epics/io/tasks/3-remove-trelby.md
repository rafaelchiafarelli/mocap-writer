## 3. Remove `.trelby` from the program

- **Status:** Done (2026-10-25) — Open, Save, Save As are Fountain only; a
  `.trelby` is refused with a message; `trelby/sample.fountain` replaces
  `sample.trelby`; `short.trelby` deleted. Checked through the real window.
- **Type:** code
- **Depends on:** io/1
- **Decision (Rafael, 2026-10-25):** no script of Rafael's is in `.trelby`;
  the format goes, and the work focuses on the writer's own format
  (`initiatives/file-format/`). The per-script page setup and styles can
  still be kept with Script → Settings → Save as / Load, which do not use
  `.trelby`.
- **Contract:**
  - In: File → Open, Save, Save As, recent files, command-line scripts
  - Requires: Open and Save As offer Fountain and All files only; Save
    always writes Fountain (`.fountain` is added unless the name already
    ends in it); opening a `.trelby` shows a message
    instead of reading it; tab names drop `.fountain`; the test-mode sample
    is `trelby/sample.fountain`; `short.trelby` and `trelby/sample.trelby`
    are deleted
  - Delivers: a program that reads and writes Fountain only
- **Pre-work:** —
- **Out of scope:** `Screenplay.load` / `save`, `fileformat.txt` and
  `tests/fixtures/test.trelby`: about a hundred tests build their scripts
  from that fixture; moving them to Fountain fixtures and deleting the code
  is io/4
- **Tests:** the full suite; the GUI path (open refuses `.trelby`, Save As
  writes `.fountain`) checked by hand through the real window
