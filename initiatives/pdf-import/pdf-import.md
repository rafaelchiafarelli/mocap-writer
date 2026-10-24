# pdf-import — mocap-writer

**Status:** Done (2026-10-24) — importer epic done, merged to `main` at
Rafael's request. Open from the initiative gate: one real script imported
on its film root with every `IMPORT:` note resolved — a film session's job,
not more project work. **First initiative** (Rafael, 2026-10-24):
his existing scripts become the known starting point for everything else.

**Goal:** Rafael's existing screenplays (master-scene PDFs with selectable
text, from Final Draft, Celtx, Word and Google Docs) open in the writer and
come out as Fountain, with no LLM.

**Scope:** PDF text with positions → element by indent, the layout detected
from the PDF itself (Rafael, 2026-10-24: no profile choice; problems become
notes in the script and an import report); File → Import in the editor; a
batch CLI that writes `.fountain`. Moved here from mocap-previz `validation/fountain-input/1`
(its D7), which now consumes the result.

**Out of scope:** scanned PDFs / OCR; non-master-scene formats; saving Fountain
as the native format (fountain-native/io; export already exists:
`Screenplay.generateFountain`).

**Initiative gate:** the generated test PDFs import to their expected
Fountain, and one of Rafael's real scripts imports with every `IMPORT:`
note understood and resolved (a film session, run on its film root).

Epics: `epics/README.md`.
