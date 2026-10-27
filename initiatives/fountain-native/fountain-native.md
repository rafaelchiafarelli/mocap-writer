# fountain-native — mocap-writer

**Status:** In progress — the io epic is done (2026-10-26); scenes/1 is
ready to implement; notes/1 waits for an `annotation` message; settings/1
(was io/2) waits for file-format/layout/1 and a `script_settings` message
(`../open-points.md`).

**Goal:** Fountain is the writer's own format (mocap-previz D3/D6): it opens and
saves `.fountain` without loss, scenes have a stable identity, and notes can
cover a span of text.

**Scope:** reading/writing Fountain 1.1 in the editor, permanent scene numbers and the
numbering rule, notes on spans.

**Out of scope:** `.trelby` files (removed from the program, io/3), the
mocap-previz parser (it reads what this writes).

**Initiative gate:** the neutral sample and one real scene survive open → save
→ open byte-identical, and Rafael approves the numbering behavior.

Epics: `epics/README.md`.
