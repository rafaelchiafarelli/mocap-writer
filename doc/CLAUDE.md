# doc — the user manual and architecture overview

**Role:** Source of Trelby's user manual (Help → Manual), and the
architecture overview of mocap-writer, in two forms with the same content:
`architecture.md` for AI agents and `architecture/` (HTML pages) for human
architects. Neither is as-built documentation: the manual describes what the user sees, and the
code-level docs are the `CLAUDE.md` files and `../trelby.process.md`.
**Entry points:** `trelby/manual.py` (`build`) turns `manual.xml` into HTML
with lxml and a stylesheet here each time the manual opens.
**Inputs → Outputs:** DocBook XML + XSL stylesheet → the page in the
manual window (needs the DocBook XSL stylesheets; the image has
`docbook-xsl`).
The architecture overview is built from the as-built docs by hand (no
build step); open `architecture/index.html` in a browser.

## Files
- `manual.xml` — the manual: concepts, editing, view modes, every menu
  command, import/export formats (Fountain at `doc/manual.xml:1695`).
- `version.xml` — `trelby.version` entity, `2.4.16.2` (`doc/version.xml:1`),
  pulled into `manual.xml` (`doc/manual.xml:5`).
- `html-stylesheet.xsl` — HTML stylesheet importing the DocBook XSL from
  `/usr/share/sgml/docbook/xsl-stylesheets/` (Fedora-style path).
- `html-stylesheet-deb.xsl` — the same for Debian / Ubuntu's path;
  `manual.py` picks it when `/usr/share/sgml/docbook/stylesheet/xsl/`
  exists (the Docker image).
- `architecture.md` — the architecture overview for AI agents: the map
  (parts, what each holds, its files, what it hands to whom) and one
  section per layer (model, editor, Fountain and numbers, film root,
  around the code), with traces, exercises and questions; read before the
  as-built docs (`mocap-workflow` skill, "Implementing one task").
- `architecture/` — the same overview as interactive pages for human
  architects, as published at
  https://claude.ai/artifact/KyZacNpzPJsvbTkca2gHAj (private); no code, so
  covered here:
  - `index.html` — the map (white); carries the publish wrapper the
    online copy was saved with.
  - `model.html` (blue), `editor.html` (pink), `fountain.html` (yellow),
    `film.html` (green), `around.html` (goldenrod) — one page per layer,
    each with a clickable diagram, traces and questions.
  - `style.css` — layout and the revision-page colours, light and dark.
  - `app.js` — the clickable diagram boxes (`window.BOXES`) and the
    show-answer buttons.

## Key facts / gotchas
- Nothing builds a `manual.html` or a man page any more (the `Makefile`
  and `refentry.xml` were removed 2026-10-31): Help → Manual makes the page
  from `manual.xml` (`trelby/manual.py`), so edits to this folder show at
  the next opening.
- `version.xml` duplicates the version in `trelby/misc.py:20`; nothing
  keeps them in sync.
- Out of scope for the as-built rule: the manual is user documentation, not
  updated per code change unless a task says so.
- The architecture overview **is** updated with the code: a change to the
  architecture rebuilds `architecture.md` and `architecture/` from the
  as-built docs in the same commit, and the online copy is republished
  from `architecture/` (`mocap-workflow` skill, "As-built documentation").
  Built at commit 959bc3c, updated after the 2026-10-31 bug fixes.
- The pages load Google Fonts; offline they fall back to the system fonts.

## Touchpoints
- Read by: `trelby/manual.py`; `tests/test_manual.py`.
