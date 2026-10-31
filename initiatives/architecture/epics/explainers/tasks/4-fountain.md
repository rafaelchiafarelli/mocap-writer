## 4. Fountain and scene numbers

- **Status:** Done (2026-10-31) — published privately: https://claude.ai/artifact/KyZacNpzPJsvbTkca2gHAj (page `fountain.html`), built from the as-built docs at commit 959bc3c.
- **Type:** explainer page
- **Contract:**
  - In: `trelby/fountain.as-built.md`, `trelby/scenenumbers.py`
  - Requires: parse → load → generate and the byte-identical round trip;
    the permanent scene numbers (the rule, letters, OMITTED, Renumber all,
    numbers given on save); an exercise: number an inserted scene
  - Delivers: the page
- **Tests:** the exercise checked against `scenenumbers.assign`
