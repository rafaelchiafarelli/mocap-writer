## 4. Fountain export misreads Action as scene headings

- **Status:** Fixed (2026-10-26) — fountain-native/io/5 (`5-one-fountain-path`): the code was deleted; Fountain import and export go through `fountain.load` / `generate`.
- **Symptom:** Action lines that start like `INT`/`EXT` (e.g. `INTO`, `EXTRA`) get two trailing spaces, and so does every line of an element whose text starts that way.
- **Where:** `looksLikeScene` is a bare prefix test (`trelby/screenplay.py:402-409`) and is called with the whole element `txt` (`trelby/screenplay.py:459`)
- **Reproduce:** Action "EXTRAS walk in.", export Fountain.
- **Impact:** noise in the Fountain output; other Fountain tools read the trailing spaces differently.
