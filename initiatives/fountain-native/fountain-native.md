# fountain-native — mocap-writer

**Status:** Implemented (2026-10-30) — io, scenes, notes and settings are
done; import/1 is a future feature, not scheduled; the gate waits for
Rafael (the numbering behavior and a real scene's round trip).

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
