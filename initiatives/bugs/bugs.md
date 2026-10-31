# bugs — mocap-writer

**Status:** Open — a backlog, not run in order (Rafael, 2026-10-24).

**Goal:** every known bug written down in one place, so the project keeps
moving and a bug is fixed when it gets in the way: it blocks a task, hurts a
film session, or Rafael asks (`mocap-workflow`, "Bugs").

**How a bug is fixed:** a `fixes/<id>/<name>` branch off `dev`, never this
initiative's chain. The fix commit sets the bug file's **Status** to
`Fixed (<date>) — fixes/<id>/<name>` and updates the as-built (its gotcha);
once the fix is pushed, a follow-up commit deletes the bug file and turns
every link to it into plain text (Rafael, 2026-10-26).

**Sources:** Rafael's review of unmodified Trelby (2026-10-23) and the
as-built review against the code (2026-10-24).

**Out of scope:** dead code, unused names and slow-but-correct code noted in
the as-built gotchas; they are oddities, not bugs.

Epics: `epics/README.md`.
