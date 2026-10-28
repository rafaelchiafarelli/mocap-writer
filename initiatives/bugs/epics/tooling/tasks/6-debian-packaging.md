## 6. Debian package metadata out of date

- **Status:** Won't fix (2026-10-27) — fixes/000092/tools: debian/ stays as upstream's, unused by Mocap Studio (Rafael)
- **Symptom:** Run dependencies lack `python3-reportlab`; `icon256.png` goes to `/usr/share/resources`, so `Icon=trelby256` is not found; the description lists only `.fdx`/`.celtx` imports.
- **Where:** `debian/control:12`, `debian/control:31-33`, `debian/install:1`, `trelby/resources/trelby.desktop`
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** a .deb install would miss PDF export and the icon.
