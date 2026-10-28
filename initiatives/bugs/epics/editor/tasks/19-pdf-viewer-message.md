## 19. "PDF viewer not found" message shows a literal %s

- **Status:** Fixed (2026-10-27) — fixes/000090/editor-more
- **Symptom:** When the configured PDF viewer is missing, the message ends with "Using the default PDF viewer instead:" followed by `%s` instead of the viewer's path.
- **Where:** the message mixes `{}` and `%s` and gets two `.format` arguments (`trelby/util.py:1297-1300`).
- **Reproduce:** Found by reading the code while fixing config-i18n/3 (2026-10-27).
- **Impact:** cosmetic.
- **Likely fix:** `%s` → `{}`; the msgid changes, so `po/*.po` need the new msgid and `t_03_build.sh` (gettext tools are not in the Docker image).
