# docker — the mocap-writer image: run Trelby and its tests without touching the host

**Role:** The environment Trelby runs in under Mocap Studio's
`DEPENDENCIES.md` rule: Ubuntu 24.04 pinned by digest, system Python 3.12, a
venv built only from a hashed lockfile. The source is not copied into the
image; the scripts mount the repository read-only at `/app`.
**Entry points:**
- `docker/run.sh [work-dir]` — start the editor on the host display.
- `docker/test.sh [pytest args]` — run the test suite (no display needed).
**Inputs → Outputs:** `Dockerfile` + `requirements.lock` → image
`mocap-writer:dev`; repository + work dir → a running Trelby window, or a
pytest result.

## Files
- `Dockerfile` — `ubuntu:24.04@sha256:…`; apt installs Python, GTK3 and the
  libraries the prebuilt wxPython wheel links against, DejaVu and Liberation
  fonts; `/opt/venv` from `requirements.lock` with `--require-hashes`,
  wxPython from the `extras.wxpython.org` Ubuntu 24.04 wheels;
  `XDG_CONFIG_HOME=/config`, `GSETTINGS_BACKEND=memory`, user `ubuntu`,
  default command `python /app/trelby.py` (`docker/Dockerfile:5-25`).
- `requirements.in` — direct dependencies: `wxPython==4.2.5`, `lxml`,
  `reportlab`, `pytest`.
- `requirements.lock` — hashed lock of 10 packages (wxPython 4.2.5, lxml
  6.1.3, reportlab 5.1.0, pillow 13.0.0, pytest 9.1.1, …).
- `run.sh` — builds the image if it does not exist, then runs it as the host
  user with the repo at `/app:ro`, the work dir at `/work`,
  `~/.config/mocap-writer` at `/config`, and X11 or WSLg display sockets
  (`docker/run.sh:12-44`); when the config holds `Theme:1` (Dark) it adds
  `GTK_THEME=Adwaita:dark` so menus, toolbar and dialogs are dark
  (`docker/run.sh:30-35`).
- `test.sh` — rebuilds the image quietly (cached), then
  `python -m pytest -p no:cacheprovider` in `/app` (`docker/test.sh:6-12`).

## Key facts / gotchas
- `run.sh` builds only when the image is missing
  (`docker/run.sh:18-20`): after a lockfile change, run `test.sh` once (it
  always builds) or `docker build` by hand, or `run.sh` keeps the old image.
- The repository is mounted read-only, so the program cannot write next to
  its code; Trelby writes only to `$XDG_CONFIG_HOME/trelby` (`/config`),
  the work dir and temp files.
- `-p no:cacheprovider` because `/app` is read-only.
- The image has no DocBook toolchain, so `trelby/manual.html` is never
  built in it.
- Upstream's `../requirements.txt` and the GitHub workflow still install
  unpinned packages; the lockfile here is what Mocap Studio uses.

## Touchpoints
- Used by: whoever runs or tests the program; `tests/CLAUDE.md`.
- Depends on: Docker on the host; for the GUI, WSLg (`/mnt/wslg`) or an X11
  display.
