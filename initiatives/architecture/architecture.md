# architecture — mocap-writer

**Status:** Planned (2026-10-30). Asked by Rafael, 2026-10-30: "an
initiative to learn about the architecture of this project".

**Goal:** Rafael learns how mocap-writer is built, well enough to read a
change, place a new feature and judge a design proposal: the screenplay
model inherited from Trelby, the wx editor around it, Fountain as the
native format, the film root and its records, and the contracts with the
rest of Mocap Studio.

**Decided (Rafael, 2026-10-30):** mocap-writer first (the other
repositories may follow); the form is **interactive explainer pages**:
private web pages with diagrams to click through, each ending with a few
questions or a small exercise, built from the as-built docs
(`trelby.process.md`, the `CLAUDE.md` of each folder) so they describe the
code as it is.

**Scope:** one page per topic (epic `explainers`), each pointing to the
`file:line` it explains, and a map page linking them.

**Out of scope:** changing code; documenting other repositories; a
replacement for the as-built docs (the pages explain, the docs record).

**Rule:** a page names the commit it was built from; when the code it
explains changes, the page is rebuilt from the as-built docs, never edited
from memory.

**Initiative gate:** Rafael goes through the pages and can trace one
action (typing a scene heading, saving, Find props) from the key press to
the files on disk.

Epics: `epics/README.md`.
