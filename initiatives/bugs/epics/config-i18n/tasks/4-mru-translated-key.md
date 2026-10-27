## 4. Recent files saved under a translated key

- **Status:** Fixed (2026-10-27) — fixes/00008b/i18n-keys
- **Symptom:** Switching `$LANG` loses the recent-files list.
- **Where:** `v.addList("files", [], _("Files"), …)` (`trelby/globaldata.py:70`)
- **Reproduce:** open files in English, restart with `LANG=it`.
- **Impact:** MRU list lost.
