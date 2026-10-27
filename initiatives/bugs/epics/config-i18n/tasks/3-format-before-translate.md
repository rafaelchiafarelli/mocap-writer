## 3. Messages formatted before translation

- **Status:** Fixed (2026-10-27) — fixes/00008b/i18n-keys
- **Symptom:** `_("...{}".format(x))` looks up the formatted string, so those messages are never translated.
- **Where:** throughout, e.g. `trelby/trelbyctrl.py:965`, `trelby/config.py:1319`
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** untranslated messages in non-English locales.
- **Likely fix:** `_("...{}").format(x)`.
