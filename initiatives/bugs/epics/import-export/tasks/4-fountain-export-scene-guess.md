## 4. Fountain export misreads Action as scene headings

- **Status:** Open
- **Symptom:** Action lines that start like `INT`/`EXT` (e.g. `INTO`, `EXTRA`) get two trailing spaces, and so does every line of an element whose text starts that way.
- **Where:** `looksLikeScene` is a bare prefix test (`trelby/screenplay.py:658-665`) and is called with the whole element `txt` (`trelby/screenplay.py:715`)
- **Reproduce:** Action "EXTRAS walk in.", export Fountain.
- **Impact:** noise in the Fountain output; other Fountain tools read the trailing spaces differently.
