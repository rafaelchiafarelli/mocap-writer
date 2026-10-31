# mocap-writer — Trelby fork, the script editor of Mocap Studio

**Role:** The repository root: the launcher, upstream Trelby's packaging and
translation scripts, and one folder per concern. The program is the
`trelby/` package; what it does stage by stage is in `trelby.process.md`.
Planning lives in `initiatives/`, process in
`.claude/skills/mocap-workflow/`.
**Entry points:**
- `docker/run.sh [work-dir]` — the Mocap Studio way to run the editor;
  `docker/test.sh [pytest args]` runs the test suite (see `docker/CLAUDE.md`).
- `trelby.py` — imports `trelby.trelby` and calls `main()`
  (`trelby.py:4-6`); command-line flags in `trelby.process.md`, "Inputs".
- `make dist` / `make test` / `make clean` (`Makefile:3,22,18`).
**Inputs → Outputs:** source tree → the running editor (Docker), a test run,
or upstream's packages (PyPI from `setup.cfg`, `.deb` from `debian/`,
Chocolatey from `choco/`).

## Files
- `CLAUDE.md` — this file.
- `trelby.process.md` — stage-by-stage spec of the program.
- `trelby.py` — launcher run from the source tree.
- `README.md` — why the fork exists, how to run it with Docker, then
  upstream's README.
- `README.dev` — upstream's developer notes: data-file preparation
  (`make dist`), a Windows build (marked out of date), test mode.
- `TODO` — upstream's to-do list (version in too many places, undo tests).
- `TRANSLATION_NOTES.txt` — upstream's steps for translators: the three
  `t_0*.sh` scripts, then a pull request.
- `LICENSE` — GPL-2.0 text.
- `Makefile` — `dist` gzips `trelby/names.txt` and `trelby/dict_en.dat` and
  builds `trelby/manual.html` and `trelby/trelby.1.gz` through `doc/`
  (`Makefile:3-16`); `clean`; `test` runs `pytest` (`Makefile:22-23`).
- `pyproject.toml` — setuptools build backend; pytest collects `tests/`
  only (the submodule has its own suite).
- `.gitmodules` — `third_party/mocap-contracts`.
- `setup.cfg` — PyPI metadata: name `trelby`, version `2.4.16.2`
  (`setup.cfg:3`), Python `>=3.11`, dependencies `wxPython`, `lxml`,
  `reportlab`, `pdfplumber` (`setup.cfg:16-22`), console script `trelby`
  (`setup.cfg:26`), package data (`setup.cfg:28-38`).
- `requirements.txt` — upstream's unpinned pip list (`pdfplumber` added
  2026-10-26), used by the GitHub
  workflow (`.github/workflows/CLAUDE.md`); Mocap Studio uses
  `docker/requirements.lock` instead.
- `long_description.txt` — PyPI long description (`setup.cfg:8`).
- `t_01_update_pot.sh` — `xgettext` over `trelby/*.py` into
  `po/trelby.pot`.
- `t_02_update_po.sh` — `msgmerge` the `.pot` into every `po/*.po`.
- `t_03_build.sh` — `msgfmt` every `po/<lang>.po` into
  `trelby/locales/<lang>/LC_MESSAGES/trelby.mo`.
- `t.bat` — `python3 trelby.py --test trelby/sample.fountain` (Windows).
- `icon32.ico` — Windows icon (256/64 px images); only `debian/copyright`
  names it, no build step uses it.
- `.travis.yml` — upstream's old Travis CI (`make test`); Travis is not used.
- `.gitignore` — editor backups, bytecode, `.trelby/`, `*.trelby`, `.tox/`,
  `/venv/`, `/.vscode/`, `*.nupkg`.

## Folders
- `trelby/` — the application package (`trelby/CLAUDE.md`).
- `tests/` — pytest suite (`tests/CLAUDE.md`).
- `docker/` — image, run and test scripts (`docker/CLAUDE.md`).
- `doc/` — DocBook manual and man page (`doc/CLAUDE.md`).
- `po/` — translation sources (`po/CLAUDE.md`).
- `media/` — upstream artwork (`media/CLAUDE.md`).
- `resources_mac/` — macOS icon (`resources_mac/CLAUDE.md`).
- `choco/`, `debian/` — upstream packaging (their `CLAUDE.md`).
- `.github/` — holds only `workflows/` (`.github/workflows/CLAUDE.md`).
- `third_party/mocap-contracts/` — git submodule pinned to a tag
  (`v0.7.0`): the film root formats (`film.harpia`, `bible.harpia`,
  `change.harpia`, `script_settings.harpia`, `annotation.harpia`,
  `scene_index.harpia`, `change_set.harpia`, `front_matter.harpia`); on `PYTHONPATH` in the image (`docker/Dockerfile`), not
  installed, since a hashed lock can't hold a `git+` URL. Its own docs
  are inside it.
- `initiatives/` — planning: initiatives, epics, tasks, the bug backlog
  (`initiatives/README.md`).
- `.claude/skills/mocap-workflow/` — the Mocap Studio process skill, a copy
  of `mocap-studio/.claude/skills/mocap-workflow/`.

## Key facts / gotchas
- **Version in many places:** `setup.cfg:3`, `trelby/misc.py:20`,
  `choco/`, `doc/version.xml`, `debian/changelog`, and the
  `--package-version` in `t_01_update_pot.sh:4`; nothing keeps them in sync.
- `README.dev` sections 3–4 describe upstream's old layout (`bin/trelby`,
  `sample.trelby`). What `--test` does now: no splash, config under
  `./.trelby` (`trelby/misc.py:49-51`), and the hotkeys `å` / `¤` / `½`
  (`trelby/trelbyctrl.as-built.md`).
- `make dist` needs the DocBook toolchain, which the Docker image does not
  have (`docker/CLAUDE.md`).

## Touchpoints
- Upstream: `git fetch upstream && git merge upstream/master`
  (`upstream` = `https://github.com/trelby/trelby.git`), from `README.md`.
- Mocap Studio: `mocap-studio` holds this repository as a submodule.
