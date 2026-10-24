# pdf-import — mocap-writer

**Status:** Planned — not started. **First initiative** (Rafael, 2026-10-24):
his existing scripts become the known starting point for everything else.

**Goal:** Rafael's existing screenplays (master-scene PDFs with selectable
text, from Final Draft, Celtx, Word and Google Docs) open in the writer and
come out as Fountain, with no LLM.

**Scope:** PDF text with positions → element by indent, from a declared
layout profile per source program; File → Import in the editor; a batch CLI
that writes `.fountain`. Moved here from mocap-previz `validation/fountain-input/1`
(its D7), which now consumes the result.

**Out of scope:** scanned PDFs / OCR; non-master-scene formats; saving Fountain
as the native format (fountain-native/io; export already exists:
`Screenplay.generateFountain`).

**Initiative gate:** each neutral fixture imports to its expected Fountain,
and one of Rafael's real scripts imports with no unknown-indent stop left
(a film session, run on its film root).

Epics: `epics/README.md`.
