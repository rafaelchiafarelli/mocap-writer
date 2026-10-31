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

## Outputs

What you find on disk after working in mocap-writer, and what a program
or AI agent reading it can count on. The editor works on a **film root**:
a folder made by File → New film or Import into film. Everything it
writes there is UTF-8 text: the script is Fountain, every other file is
JSON in a `mocap-contracts` format (pinned in `third_party/`), read and
written with the `mocap_contracts` package.

```
<film-root>/
  film.json                      index: the parts, who owns each, id spaces
  script.fountain                the screenplay (Fountain 1.1)
  settings/script-settings.json  page setup, element styles, title layout
  settings/front-matter.json     title page, overview, pitch, argument
  bible/
    sets/ characters/ props/ wardrobe/
      <slug>/item.json           one bible item; photos and child items beside it
    not-props.json               capitalized words marked "not a prop"
    scene-index.json             the accepted scene index (for agents)
    sync/last-sync.json          the scene index of the last accepted sync
    sync/<time>-changes.json     one change set per Sync to spec
  annotations/annotation-*.json  notes and shots, anchored by scene and quote
  history/<yyyy-mm>.jsonl        change log: every record edit, before and after
  ids/w.json                     the writer's id counters
  source/<file>                  the original of an imported script
```

| File | Written when | Read by |
|---|---|---|
| `script.fountain` | Save | any Fountain tool; the agents |
| `bible/**/item.json` | bible panel edits, Find props / sets / characters, a review decision | the agents; the review view |
| `bible/scene-index.json` | Sync to spec (F5), then **Accept** | the agents |
| `bible/sync/<time>-changes.json` | every Sync to spec run, accepted or not | the agents |
| `annotations/`, `settings/` | edits in the editor | the editor |
| `history/` | every write except the script and the sync files | Revert; reject in the review view |

**What a reader can count on:**

- **Scene numbers are permanent.** Written in the heading as `#12#`,
  `#12.A#`; a deleted scene stays as `.OMITTED #n#`. Everything else (the
  bible, the index, annotations) points to scenes by this number, never by
  position or heading text.
- **Ids are permanent.** A record id is `<kind>-<space>-<n>` (e.g.
  `prop-w-3`); renaming an item renames its folder, not its id.
- **Every bible value carries a state**: `script-stated`,
  `creator-approved`, `proposal` or `tbd`, plus its source and author. Only
  the creator turns a `proposal` into `creator-approved`, in Script →
  Review proposals.
- **The scene index is built by code, not by AI**: per numbered scene its
  INT/EXT, location, time of day, set id, characters (speaking or only
  named in Action), prop words (runs of capitals in Action), page and line
  range, and a SHA-256 of its text. Nothing is inferred beyond the script
  and links the creator already made.
- **A change set lists what changed since the last accepted sync**, scene
  by scene: added, removed, moved, heading or text changed, character
  entered or left, prop added or removed, set link changed.
- **Invalid files are refused, not repaired.** A file that breaks its
  contract is never written and is reported on open.
- **The writer owns its parts.** `bible/` and the other parts in
  `film.json` are the writer's; another program gets its own id space and
  `proposals-<code>` part, never writes into `bible/` directly.
- **Fountain round trip:** open → save changes only what was edited;
  boneyard, sections and synopses are kept. In a film the title block is
  written from `settings/front-matter.json`. Act breaks are
  `# Act name`, notes `[[…]]`, a Shot an upper-case line ending in two
  spaces (other Fountain tools read it as Action).

**Outside the film root**

- Export (File → Export): PDF, RTF, Final Draft (`.fdx`), HTML, Fountain,
  formatted text; Watermark writes one PDF per line of its list.
- Print, reports (script, scene, location, character, dialogue chart) and
  Compare scripts: a PDF in a temporary file, opened in the viewer.
- PDF import from the command line:
  `docker/pdfimport.sh import <pdf>... --out <dir>` writes one
  `.fountain` per PDF; doubtful spots become `[[IMPORT: …]]` notes.
- Settings: `~/.config/mocap-writer` on the host (global config, window
  state, recent files, the personal dictionary).

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
