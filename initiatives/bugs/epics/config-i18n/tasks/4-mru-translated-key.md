## 4. Recent files saved under a translated key

- **Status:** Open
- **Symptom:** Switching `$LANG` loses the recent-files list.
- **Where:** `v.addList("files", [], _("Files"), …)` (`trelby/globaldata.py:70`)
- **Reproduce:** open files in English, restart with `LANG=it`.
- **Impact:** MRU list lost.
