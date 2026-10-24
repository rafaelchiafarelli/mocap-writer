# fountain-native — mocap-writer

**Status:** Planned — not started.

**Goal:** Fountain is the writer's own format (mocap-previz D3/D6): it opens and
saves `.fountain` without loss, scenes have a stable identity, and notes can
cover a span of text.

**Scope:** reading/writing Fountain 1.1 in the editor, scene ids and the
numbering rule, notes on spans.

**Out of scope:** `.trelby` files (still open, never the default), the
mocap-previz parser (it reads what this writes).

**Initiative gate:** the neutral sample and one real scene survive open → save
→ open byte-identical, and Rafael approves the numbering behavior.

Epics: `epics/README.md`.
