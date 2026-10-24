# doc — the user manual and man page (DocBook sources)

**Role:** Sources of Trelby's user manual (HTML) and Unix man page. Not
as-built documentation: the manual describes what the user sees, and the
code-level docs are the `CLAUDE.md` files and `../trelby.process.md`.
**Entry points:** `make -C doc html` → `manual.html`; `make -C doc manpage`
→ `trelby.1.gz` (`doc/Makefile`). The root `Makefile` moves both into
`trelby/` for packaging (`Makefile:12-16`).
**Inputs → Outputs:** DocBook XML + XSL stylesheets → `manual.html`,
`trelby.1.gz` (needs `xsltproc` and the DocBook XSL stylesheets installed).

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

## Key facts / gotchas
- The built `manual.html` is not in git and not in the Docker image, so
  Help → Manual opens a missing file (`trelby/trelbyframe.py:972`). Bug: [bugs/editor/11](../initiatives/bugs/epics/editor/tasks/11-help-manual-missing.md).
- `version.xml` duplicates the version in `trelby/misc.py:20`,
  `setup.cfg` and `choco/trelby.nuspec`; nothing keeps them in sync.
- Out of scope for the as-built rule: the manual is user documentation, not
  updated per code change unless a task says so.

## Touchpoints
- Built by: root `Makefile`, `debian/rules` (`make -C doc manpage html`).
- Installed by: `debian/install`, `debian/links`, `setup.cfg`
  (`manual.html`, `trelby.1.gz` as package data).
