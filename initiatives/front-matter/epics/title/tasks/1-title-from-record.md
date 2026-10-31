## 1. The title block from the record

- **Status:** Done (2026-10-31) — `frontmatter.titleBlock` / `fromBlock` / `applyTitle` / `syncTitle`, on every save of a film's script and on open; Title pages… points to the front matter in a film; checked through the real window.
- **Type:** code
- **Depends on:** record/1
- **Contract:**
  - In: a film's script and its front matter record
  - Requires: on save of a film's script, the `.fountain` title block is
    written from the title page fields: `Title`, `Subtitle`, `Episode`,
    `Credit: Written by`, `Author` (author then co-authors, one per line;
    `Authors` when more than one), `Contact` (the e-mail); empty fields
    are left out; an empty title page writes no block. The title pages
    (`sp.titles`) are built from the record with the layout of
    `fountain.makeTitles`; in a film, Title pages… says the title page is
    edited in the front matter and opens it. A film whose record has an
    empty title page and whose script has a title block takes the block
    into the record once, on open (no title is lost)
  - Delivers: the writing, the reading on open, tests, the as-built
- **Pre-work:** none
- **Tests:** record → block text; block → record; a film opened with a
  block and no record keeps it; outside a film nothing changes
