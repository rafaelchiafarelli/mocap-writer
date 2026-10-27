## 2. Two settings pages crash outside English

- **Status:** Fixed (2026-10-27) — fixes/00008b/i18n-keys
- **Symptom:** With `LANG=it`, the Misc and Elements (global) settings pages raise `AttributeError`.
- **Where:** `setattr(self, name + _("Entry"), …)` (`trelby/configpages/miscpanel.py:150`) and `name + _("Combo")` (`trelby/configpages/elementsglobalpanel.py:64`) translate attribute names (`po/it.po`)
- **Reproduce:** `LANG=it`, open global settings.
- **Impact:** settings unusable in Italian.
- **Likely fix:** drop the `_()` around the suffixes.
- **Fix:** fixed keys; the same bug also hit the Elements (script) and Paper pages (`addCheckBox`, `addMarginCtrl`), which now take a key and a label; `tests/test_i18n.py`.
