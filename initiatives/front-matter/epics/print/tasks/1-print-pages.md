## 1. The pages printed before the script

- **Status:** Done (2026-10-31) — `frontmatter.addPages` / `overviewLines` / `titlePages`, `Screenplay.frontPages` set by `MyCtrl.makePDF`; checked through the real window (a sample PDF in the review folder).
- **Type:** code
- **Depends on:** record/1, title/1; `acts.actsOf`; the bible
- **Contract:**
  - In: the script, its film's record and bible
  - Requires: the PDF (export and print) puts after the title page, in
    order, each included page: the **overview** (Cast: the bible's
    characters by name; Sets: the bible's sets with their child sets
    indented; Acts: each act with its scene numbers and its page range,
    from `acts.actsOf` and the pagination); the **pitch** (Pitch, Logline,
    Target audience); the **argument** (as many pages as its text needs,
    laid out by `pml.TextFormatter`). Left-out pages are not printed;
    page numbers of the script do not change (the front pages are not
    counted, as title pages are not)
  - Delivers: the pages, tests, the as-built
- **Pre-work:** none
- **Tests:** each page's PML text on the neutral sample made a film;
  include off → page gone; a long argument runs over two pages; the
  script's first page is still page 1
