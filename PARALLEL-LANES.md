# Parallel lanes — work for other sessions (2026-10-27)

Lanes that run in their own clones while the original session works
on **fountain-native/scenes** in its own clone. Each lane follows the
`mocap-workflow` skill (`.claude/skills/mocap-workflow/SKILL.md`): one
initiative chain per clone, the task file is the contract, the full test
suite passes, the as-built docs travel with the change, and anything
outside the task's contract is a stop-and-ask.

**Not yours:** `initiatives/fountain-native/` and the scene-number code
(`trelby/fountain.py`, `trelby/screenplay.py`, `trelby/trelbyctrl.py`
for scene headings) belong to the scenes session. Don't edit them. If a
lane needs a change there, write it down and ask Rafael.

When a lane is done, its session deletes its section from this file in
its last merge to `dev`. The session that empties the file deletes it
and its bullet in `CLAUDE.md`.

---

## Lane B — spellcheck/study/1: the pt-BR dictionary study

- **Repository / clone:** `mocap-writer`, a new clone of `dev`.
- **Task file:** `initiatives/spellcheck/epics/study/tasks/1-dictionary-study.md`
  (contract, options and measurements are all written there). Context:
  `initiatives/spellcheck/spellcheck.md`.
- **Chain:** `dev → features → spellcheck → epics → study → tasks →
  1-dictionary-study`.
- **Type:** a study. Measurements happen in a throwaway container (start
  from the writer's image, `docker/CLAUDE.md`). Nothing changes in
  `trelby/`, the Dockerfile or `docker/requirements.lock`.
- **Licence rule:** commercial use must be allowed (MIT, Apache-2.0, BSD,
  CC0, CC-BY; GPL-family for tools). Check the dictionary files' own
  licence, not only the engine's. Anything else goes to Rafael with the
  facts.
- **Text samples:** neutral text only, never film material
  (`tests/fixtures/fountain/sample_ptbr.fountain` plus a longer neutral
  text).
- **Delivers:** the options table and a recommendation, written into the
  task file, with the commands that reproduce every measurement. Then stop:
  Rafael decides, the decision is written in the task file, and only then
  is `pt-br/1` planned and implemented.
- **Done:** the study is merged up to `dev` with the task marked done
  (the gate is Rafael's decision). Remove its line under "Ready to
  implement" in `initiatives/open-points.md`, and update the spellcheck
  status lines.
