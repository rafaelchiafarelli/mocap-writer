# docker — the mocap-writer image: run Trelby and its tests without touching the host

**Role:** The environment Trelby runs in under Mocap Studio's
`DEPENDENCIES.md` rule: Ubuntu 24.04 pinned by digest, system Python 3.12, a
venv built only from a hashed lockfile. The source is not copied into the
image; the scripts mount the repository read-only at `/app`.
**Entry points:**
- `docker/run.sh [work-dir]` — start the editor on the host display.
- `docker/test.sh [pytest args]` — run the test suite (no display needed).
- `docker/pdfimport.sh probe|import ...` — the PDF importer's command line
  (`python -m trelby.pdfimport`) on files in the current directory.
**Inputs → Outputs:** `Dockerfile` + `requirements.lock` → image
`mocap-writer:dev`; repository + work dir → a running Trelby window, or a
pytest result.

## Files
- `Dockerfile` — `ubuntu:24.04@sha256:…`; apt installs Python, GTK3 and the
  libraries the prebuilt wxPython wheel links against, DejaVu and Liberation
  fonts, `evince` (GPL-2.0+; the PDF viewer for Print and reports) and
  `docbook-xsl` (permissive DocBook XSL licence; Help → Manual); `/opt/venv` from `requirements.lock` with `--require-hashes`,
  wxPython from the `extras.wxpython.org` Ubuntu 24.04 wheels;
  `XDG_CONFIG_HOME=/config`, `GSETTINGS_BACKEND=memory`, user `ubuntu`,
  default command `python /app/trelby.py` (`docker/Dockerfile:5-25`).
- `requirements.in` — direct dependencies: `wxPython==4.2.5`, `lxml`,
  `reportlab`, `pytest`, `pdfplumber` (for pdf-import; MIT, its
  `pdfminer.six` MIT and `pypdfium2` Apache-2.0/BSD-3).
- `requirements.lock` — hashed lock of 16 packages (wxPython 4.2.5, lxml
  6.1.3, reportlab 5.1.0, pillow 13.0.0, pytest 9.1.1, pdfplumber 0.11.10,
  pdfminer.six 20260107, pypdfium2 5.14.0, …). Regenerated with uv run
  from its image (no uv on the host): `docker run --rm --user "$(id -u):$(id -g)"
  -e HOME=/tmp -v "$PWD":/w -w /w ghcr.io/astral-sh/uv:0.8.22-python3.12-bookworm-slim`
  followed by the command in the lock's header plus `--find-links
  https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-24.04/`
  (the header omits it because of `--no-emit-find-links`); existing pins
  are kept.
- `run.sh` — rebuilds the image quietly (cached, as `test.sh`), then runs it as the host
  user with the repo at `/app:ro`, `~/.config/mocap-writer` at `/config`,
  X11 or WSLg display sockets, every Windows drive `/mnt/<letter>`, the
  host home `$HOME` and the work dir **at their own paths**
  (`docker/run.sh:48-69`), so the file dialogs show the same paths as WSL
  and every folder under the home can be written (bugs/tooling/8); `MOCAP_WRITER_WORK_DIR` = the work
  dir makes the dialogs start there (`trelby/trelby.py:102-108`). When the
  config holds `Theme:1` (Dark) it adds `GTK_THEME=Adwaita:dark` so menus,
  toolbar and dialogs are dark (`docker/run.sh:34-39`); a host
  `MOCAP_WRITER_PDF_TRACE` (a WSL path) is passed through
  (`docker/run.sh:41-46`) for the instrumented PDF import.
- `pdfimport.sh` — rebuilds the image quietly, then runs
  `python -m trelby.pdfimport "$@"` with the current directory mounted at
  its own path (also the working directory) and the repo at `/app:ro`
  (`docker/pdfimport.sh:9-15`); starter profiles are at
  `/app/trelby/pdfprofiles/`.
- `test.sh` — rebuilds the image quietly (cached), then
  `python -m pytest -p no:cacheprovider` in `/app` (`docker/test.sh:6-12`).

## Key facts / gotchas
- Every script rebuilds the image on start; Docker's cache makes that
  instant unless `docker/` changed (`docker/run.sh:22-24`).
- The container has no desktop to hand files to: PDFs open in `evince`
  through WSLg / X11 (`util.getPDFViewer`, `trelby/util.py:1217-1222`), and
  the manual is shown inside the editor (`trelby/manual.py`). The 2026-10-27
  image is about 1.5 GB.
- The repository is mounted read-only, so the program cannot write next to
  its code; Trelby writes only to `$XDG_CONFIG_HOME/trelby` (`/config`),
  the work dir, the host home, the Windows drives and temp files.
- A work dir inside a Windows drive or the home is mounted twice (the
  drive or home and the dir itself, same path); Docker allows the nested
  mount.
- Without the home mount, the folders above the work dir were empty
  root-owned stand-ins Docker creates for a mount point: visible in the
  dialogs, not writable, not the host's folders (bugs/tooling/8, fixed
  2026-10-25).
- The container sees the whole host home read-write (as the host user):
  the editor can open and save anywhere under it, like a native program.
- `-p no:cacheprovider` because `/app` is read-only.
- `trelby/manual.html` is still never built in the image (the repo is
  read-only); Help → Manual makes the page from `doc/manual.xml` with lxml
  and `docbook-xsl` each time it opens (`trelby/manual.py`).
- Upstream's `../requirements.txt` and the GitHub workflow still install
  unpinned packages; the lockfile here is what Mocap Studio uses.

## Touchpoints
- Used by: whoever runs or tests the program; `tests/CLAUDE.md`.
- Depends on: Docker on the host; for the GUI, WSLg (`/mnt/wslg`) or an X11
  display.
