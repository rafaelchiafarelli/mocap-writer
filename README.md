# mocap-writer

The script editor of Mocap Studio: a fork of the Trelby screenplay writer
(GPL-2.0), in Python.

**Why a fork of Trelby.** Mocap Studio turns a film's script into a shot
list, 3D blocking and storyboards, and the script is the source of truth for
all of that. We want it written in a real screenwriting tool whose output is
**Fountain**, a plain-text format our own parser reads and git can diff.
Trelby is the open-source editor that fits the project: it is Python (the
project's language), runs on Windows and Linux, and its GPL-2.0 license
allows commercial use. Proprietary tools such as Celtx were rejected because
they keep the script in a closed format on their servers. This fork stays
under GPL-2.0.

## What mocap-writer adds

- Fountain as the native format, saved byte for byte where nothing changed.
- Permanent scene numbers (`12`, `12.A`, `OMITTED`); records follow moved scenes.
- PDF import of existing scripts into Fountain, with a report of doubtful spots.
- A film is a folder of checked records (`mocap-contracts`, Harpia), with a change log.
- The film bible: sets, characters, props and wardrobe, linked to scenes.
- Annotations and shots kept outside the script text, anchored by scene and quote.
- Sync to spec (F5): scene index and change sets for the pre-production agents.
- Review of the agents' proposals: approve, reject or edit.
- Acts as markers, with a panel of act sizes.
- Front matter: title page, overview, pitch and argument pages.
- Import into film: the original kept, the bible reviewed, a report.
- Brazilian Portuguese spell checking (Hunspell pt-BR).
- Editor: zoom, dark theme, Tab order, horizontal scrolling.
- Runs and is tested in Docker, from a hashed lockfile.

How it is built: `doc/architecture/index.html` (for people) and
`doc/architecture.md` (for AI agents). Planning lives in `initiatives/`,
process in `.claude/skills/mocap-workflow/`.

## From source

Only Docker is needed on the host (Windows 11 with WSL2, or a Linux
desktop); nothing else gets installed.

```bash
git clone --recurse-submodules git@github.com:rafaelchiafarelli/mocap-writer.git
cd mocap-writer
docker/run.sh [work-dir]   # builds the image on first use, then opens the window
docker/test.sh             # runs the test suite
```

`work-dir` (default: the current directory) is where scripts and films are
opened and saved; settings persist in `~/.config/mocap-writer`. The image
(`docker/Dockerfile`, hashed `docker/requirements.lock`) holds only the
environment: the repository is mounted, so code edits need no rebuild. A
clone made without `--recurse-submodules` needs
`git submodule update --init` once (`third_party/mocap-contracts`).
