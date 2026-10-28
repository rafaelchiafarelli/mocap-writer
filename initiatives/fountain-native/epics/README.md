# fountain-native — epics (execution order)

1. **io** — open and save Fountain as the native format (done 2026-10-26:
   1 done 2026-10-24; 3, remove `.trelby`, and 4, tests off `.trelby`, done
   2026-10-25; 2, per-script settings, moved to the `settings` epic on
   2026-10-26; 5, one Fountain reader and writer, done 2026-10-26)
2. **scenes** — permanent scene numbers, letters for inserts (5 tasks, split
   2026-10-27: 1 the rule, 2 the number in the model and the file, 3 numbers
   given on save with OMITTED and Renumber all, 4 numbers on screen and the
   click warning, all done 2026-10-27; 5, rewriting records on a move,
   waits for the first records that name scenes)
3. **notes** — notes on spans of text (1 task; annotations kept outside the script, decided 2026-10-26, waits for the
   `annotation` message)
4. **settings** — per-script settings as a record in the film root (1 task,
   was io/2; fields approved 2026-10-26; waits for file-format/layout/1 and
   a `script_settings` message)

5. **import** — future features for Import → Fountain (1 task: the old
   importer's options; not scheduled, not part of the initiative gate)

`scenes`, `notes`, `settings` and `import` need `io`. Cross-repository: `scenes` keeps
mocap-previz `fountain-input/2` ("scene number as the scene identity") true.
