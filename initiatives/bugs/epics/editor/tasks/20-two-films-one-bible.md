## 20. Two films open, one bible

- **Status:** Fixed (2026-10-31) — fixes/0000a3/one-film-per-tab
- **Symptom:** With two films open, the bible panel kept the second film's
  bible when the first film's tab was selected: the scene line under the
  buttons followed the tab, the tree and the forms did not.
- **Where:** the frame held a single film, bible and annotations, replaced
  by each Open film (`setFilm`); `OnPageChange` never switched them back.
  The bible commands read the current tab's script and wrote into that one
  bible, so From script… in the first film's tab wrote the first film's
  scenes into the second film's bible; Save on exit skipped the settings
  and scene renames of every film but the last opened.
- **Reproduce:** Open film A, Open film B, select A's tab: the tree shows
  B's items (Rafael, 2026-10-31, with two of his films).
- **Impact:** wrong data shown, and links written into the wrong film.
- **Fix:** every open film is kept (`trelby/openfilms.py`); a tab belongs
  to the film whose script it holds, and the frame's film follows the
  current tab; a save writes its own film's records.
