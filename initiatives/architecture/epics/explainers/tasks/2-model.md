## 2. The screenplay model

- **Status:** Done (2026-10-31) — published privately: https://claude.ai/artifact/KyZacNpzPJsvbTkca2gHAj (page `model.html`), built from the as-built docs at commit 959bc3c.
- **Type:** explainer page
- **Contract:**
  - In: `trelby/screenplay.as-built.md`, `trelby/line.py`, `trelby/undo.py`
  - Requires: the script as a flat list of `Line`s (line break, element
    type, text, scene number), elements as runs of lines, the cursor and
    the mark, commands and the undo chain, pagination; one command traced
    (typing a character); an exercise: predict the lines of a two-element
    snippet
  - Delivers: the page
- **Tests:** the snippet's answer checked against the code
