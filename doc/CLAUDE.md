# doc — the user manual, man page and architecture overview

**Role:** Sources of Trelby's user manual (HTML) and Unix man page, and the
architecture overview of mocap-writer, in two forms with the same content:
`architecture.md` for AI agents and `architecture/` (HTML pages) for human
architects. Neither is as-built documentation: the manual describes what the user sees, and the
code-level docs are the `CLAUDE.md` files and `../trelby.process.md`.
**Entry points:** `make -C doc html` → `manual.html`; `make -C doc manpage`
→ `trelby.1.gz` (`doc/Makefile`). The root `Makefile` moves both into
`trelby/` for packaging (`Makefile:12-16`).
**Inputs → Outputs:** DocBook XML + XSL stylesheets → `manual.html`,
`trelby.1.gz` (needs `xsltproc` and the DocBook XSL stylesheets installed).
The architecture overview is built from the as-built docs by hand (no
build step); open `architecture/index.html` in a browser.

## Files
- `manual.xml` — the manual: concepts, editing, view modes, every menu
  command, import/export formats (Fountain at `doc/manual.xml:1695`).
- `refentry.xml` — the man page.
- `version.xml` — `trelby.version` entity, `2.4.16.2` (`doc/version.xml:1`).
- `html-stylesheet.xsl` — HTML stylesheet importing the DocBook XSL from
  `/usr/share/sgml/docbook/xsl-stylesheets/` (Fedora-style path).
- `html-stylesheet-deb.xsl` — the same for Debian's path; `Makefile` picks
  it when `/usr/share/sgml/docbook/stylesheet/xsl/` exists
  (`doc/Makefile:13-19`).
- `Makefile` — `html`, `manpage`, `clean` targets.
- `.gitignore` — ignores `book.html`.
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
- The built `manual.html` is not in git and not in the Docker image; Help →
  Manual makes the same page from `manual.xml` with lxml and the
  `html-stylesheet*.xsl` here (`trelby/manual.py`), so edits to this folder
  show at the next opening.
- `version.xml` duplicates the version in `trelby/misc.py:20`,
  `setup.cfg` and `choco/trelby.nuspec`; nothing keeps them in sync.
- Out of scope for the as-built rule: the manual is user documentation, not
  updated per code change unless a task says so.
- The architecture overview **is** updated with the code: a change to the
  architecture rebuilds `architecture.md` and `architecture/` from the
  as-built docs in the same commit, and the online copy is republished
  from `architecture/` (`mocap-workflow` skill, "As-built documentation").
  Built at commit 959bc3c, updated after the 2026-10-31 bug fixes.
- The pages load Google Fonts; offline they fall back to the system fonts.

## Touchpoints
- Built by: root `Makefile`, `debian/rules` (`make -C doc manpage html`).
- Installed by: `debian/install`, `debian/links`, `setup.cfg`
  (`manual.html`, `trelby.1.gz` as package data).
