# as-built — mocap-writer

**Status:** baseline epic done (tasks 1–3); waiting for Rafael's approval
(initiative gate). **Initiative 0** (Rafael, 2026-10-24): it
comes before `pdf-import`, so planning and code generation start from a
documented program.

**Goal:** "as-built" documentation of Trelby as it is today, saved in the
program's folders, following the model of `harpia` (one `CLAUDE.md` per
folder plus a root `<name>.process.md`). Claude Code loads a folder's
`CLAUDE.md` when it works on files there, so the right context arrives with
the code.

**Format (from harpia):**
- Root `trelby.process.md`: the stage-by-stage spec of what the program does.
- One `CLAUDE.md` per folder: `# <folder> — <purpose>`, then **Role**,
  **Entry points**, **Inputs → Outputs**, `## Files` (one bullet per file),
  `## Key facts / gotchas`, `## Touchpoints` (called by / depends on).
- Adaptation for `trelby/` (55 modules in one folder): its `CLAUDE.md` keeps
  one bullet per module; the six large modules get their detail in a sibling
  `<module>.as-built.md` (Rafael: next to the code), linked from the bullet.

**Rules:** describe what the code does, never what it should do; every claim
points to `file:line`; bugs and oddities found go under gotchas and become fix
branches, not silent edits; no code changes in this initiative.

**Out of scope:** the user manual (`doc/manual.xml` already exists);
requirements (they live in `initiatives/`).

**Initiative gate:** every folder listed in the tasks has its `CLAUDE.md`,
every module in `trelby/` has its bullet, and Rafael approves the result.
From then on, every task updates the as-built of what it changes, in the
same commit (`mocap-workflow`, step 4).

Epics: `epics/README.md`.
