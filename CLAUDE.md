# mocap-writer — Trelby fork, the script editor of Mocap Studio

**Role:** The repository root: the launcher and one folder per concern. The
program is the `trelby/` package; what it does stage by stage is in
`trelby.process.md`. Planning lives in `initiatives/`, process in
`.claude/skills/mocap-workflow/`.
**Entry points:**
- `docker/run.sh [work-dir]` — the Mocap Studio way to run the editor;
  `docker/test.sh [pytest args]` runs the test suite (see `docker/CLAUDE.md`).
- `trelby.py` — imports `trelby.trelby` and calls `main()`
  (`trelby.py:4-6`); command-line flags in `trelby.process.md`, "Inputs".
**Inputs → Outputs:** source tree → the running editor (Docker) or a test
run. What the editor writes (the film root, exports, reports) is listed in
`README.md`, "Outputs".

## Files
- `CLAUDE.md` — this file.
- `trelby.process.md` — stage-by-stage spec of the program.
- `trelby.py` — launcher run from the source tree.
- `README.md` — why the fork exists, what mocap-writer adds (one line
  each), its outputs (what a person or an agent finds after a session),
  where the architecture overview is, and From source (clone with the
  submodule, `docker/run.sh`, `docker/test.sh`); no links to upstream and
  none of upstream's README (Rafael, 2026-10-31).
- `LICENSE` — GPL-2.0 text.
- `pyproject.toml` — pytest settings only: collects `tests/` (the
  submodule has its own suite).
- `.gitmodules` — `third_party/mocap-contracts`.
- `.gitignore` — editor backups, bytecode, `.trelby/` (test-mode config),
  `/venv/`, `/.vscode/`.

## Folders
- `trelby/` — the application package (`trelby/CLAUDE.md`).
- `tests/` — pytest suite (`tests/CLAUDE.md`).
- `docker/` — image, run and test scripts (`docker/CLAUDE.md`).
- `doc/` — the DocBook user manual (Help → Manual) and the architecture
  overview: `doc/architecture.md` (for AI agents: read it first, then the
  as-built docs) and `doc/architecture/` (the same as HTML pages for
  people) (`doc/CLAUDE.md`).
- `tools/` — `add_words.py`, the English word-list script
  (`tools/CLAUDE.md`).
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
- **Upstream's packaging and tooling were removed** (Rafael, 2026-10-31,
  `fixes/0000b6/trelby-leftovers`): PyPI (`setup.cfg`, the build backend,
  `requirements.txt`), Debian, Chocolatey, the macOS icon, the `Makefile`
  and man page, Travis and GitHub CI, the translation scripts, `po/` and
  the Italian catalog, the splash artwork, upstream's `README.dev` and
  `TODO`. Mocap Studio runs and tests only through `docker/`. An upstream
  merge that touches those files is a modify/delete conflict: keep them
  deleted.
- **Version:** `trelby/misc.py:20` (the splash) and `doc/version.xml` (the
  manual); nothing keeps them in sync.
- `--test` mode: no splash, config under `./.trelby`
  (`trelby/misc.py:49-51`), and the hotkeys `å` / `¤` / `½`
  (`trelby/trelbyctrl.as-built.md`).

## Touchpoints
- Upstream: `git fetch upstream && git merge upstream/master`
  (`upstream` = `https://github.com/trelby/trelby.git`, a git remote).
- Mocap Studio: `mocap-studio` holds this repository as a submodule.
- Downstream: the `mocap-preprod` agents read the film root it writes
  (`README.md`, "Outputs").
