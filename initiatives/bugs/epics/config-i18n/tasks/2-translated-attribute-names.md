## 2. Two settings pages crash outside English

- **Status:** Open
- **Symptom:** With `LANG=it`, the Misc and Elements (global) settings pages raise `AttributeError`.
- **Where:** `setattr(self, name + _("Entry"), …)` (`trelby/configpages/miscpanel.py:150`) and `name + _("Combo")` (`trelby/configpages/elementsglobalpanel.py:66`) translate attribute names (`po/it.po`)
- **Reproduce:** `LANG=it`, open global settings.
- **Impact:** settings unusable in Italian.
- **Likely fix:** drop the `_()` around the suffixes.
