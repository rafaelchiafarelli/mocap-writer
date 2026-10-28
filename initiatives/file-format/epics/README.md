# file-format — epics (execution order)

1. **study** — requirements, candidate formats, options (3 tasks, no code;
   done 2026-10-25: Rafael chose A, a folder of Harpia JSON records,
   ISOXML-style, with C, a change log in SQLite, kept in mind; task files
   removed 2026-10-28, history: git log -- initiatives/file-format/epics/study)
2. **layout** — the root index and id scheme every part uses; history;
   missing files; open and new film; the change log (5 tasks, done in the
   order 1, 4, 3, 5; 2, the history study, decided 2026-10-28: a change
   log)

Cross-repository: `layout/1` uses `mocap-contracts` `film.harpia`
(`v0.4.0`, its five open rules in `v0.5.0`); `layout/5` uses its
`change.harpia` (`v0.5.0`, initiative `film-records` there).
