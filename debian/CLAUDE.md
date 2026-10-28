# debian — upstream Debian packaging

**Role:** Builds a `trelby` `.deb` with `dh` + pybuild. Upstream Trelby's;
Mocap Studio does not use it (it runs the program from `docker/`).
**Entry points:** `dpkg-buildpackage` → `debian/rules`.
**Inputs → Outputs:** source tree → `trelby_<version>_all.deb`, code in
`/usr/share/trelby/`, launcher in `/usr/bin`.

## Files
- `rules` — `dh $@ --with python3 --buildsystem=pybuild`; builds the man
  page and HTML manual first (`debian/rules:8-10`).
- `control` — build and run dependencies (`python3-wxgtk4.0`,
  `python3-lxml`, `python3-reportlab` to build, `python3-cryptography` to
  run) and the package description.
- `install` — extra files: `icon256.png`, `trelby.desktop`, `trelby.1.gz`.
- `links` — links the manual into `/usr/share/doc/trelby/`.
- `changelog` — top entry 2.4.16, 2025-10-03.
- `compat` — debhelper level 10.
- `copyright` — license statement.
- `source/format` — `3.0 (native)`.

## Key facts / gotchas
- **Left as upstream's on purpose** (Rafael, 2026-10-27): Mocap Studio
  runs the editor from `docker/`, so the stale metadata below is known and
  not fixed; keeping the folder unchanged eases upstream merges.
- The run dependencies list `python3-cryptography` but not
  `python3-reportlab`, which the PDF writer imports (`trelby/pdf.py:4-6`).
- `install` puts `icon256.png` in `/usr/share/resources`
  (`debian/install:1`), which no desktop environment searches.
- The description still lists only `.fdx` and `.celtx` imports.

## Touchpoints
- Uses: `setup.cfg` / `pyproject.toml` (pybuild), `doc/Makefile`,
  `trelby/resources/`.
