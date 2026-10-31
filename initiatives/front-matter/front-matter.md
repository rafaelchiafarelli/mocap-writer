# front-matter — mocap-writer

**Status:** Planned (2026-10-31). Asked by Rafael, 2026-10-31, while
deciding the Fountain import options (was fountain-native/import/1).

**Goal:** a film keeps its front matter as a record, not as text in the
script: a title page and three optional pages, edited in a form, printed
before the script, and filled from a Fountain title page on import.

**Decided (Rafael, 2026-10-31):**
- **Pages.** 1, the **title page**: title, subtitle, episode number,
  author, co-authors (as many as needed), e-mail. 2, the **overview**
  (can be left out): cast, sets, the act breakdown (pages and scenes).
  3, the **pitch** (can be left out): pitch, logline, target audience.
  4, the **argument** (can be left out, can run longer than a page).
- **Storage.** One `front_matter` record per film (a new
  `mocap-contracts` message), edited in a form like the maps' and shown
  as one node of the bible panel. Not bible maps: a map holds many items,
  a film has one front matter.
- **The Fountain title block is written from the record.** In a film the
  record is the source: on save the standard keys (Title, Credit, Author,
  Contact) and `Subtitle` / `Episode` are written into the `.fountain` so
  other tools still see a title page; the Title pages dialog no longer
  edits a film's script. A script outside a film keeps today's title
  pages (no record to hold them).
- **Printing.** The PDF export prints the included pages before the
  script. Each optional page has an **Include** tick, kept in the record
  and shown in the form. The overview is computed when printed (cast from
  the bible's characters, sets from the bible's sets, the act breakdown
  from the act markers with their pages and scenes), never typed.
- **Import options** (Import → Fountain): strip emphasis markup; sections
  and synopses as Note elements; title lines as Action; the title page
  into the front matter record (into a film).

**Scope:** the `front_matter` message; the record, its form and panel
node; the title block and title pages from the record; the printed pages;
the Fountain import options.

**Out of scope:** AI writing the pitch or argument (mocap-preprod agents);
other export formats than PDF (RTF, FDX, HTML keep the title pages as
built); a per-episode series structure.

**Initiative gate:** on the neutral sample made a film, the creator fills
the title page and the three pages, prints a PDF with the front matter
first, leaves the argument out and prints again, and the `.fountain`
shows the title block from the record.

Epics: `epics/README.md`.
