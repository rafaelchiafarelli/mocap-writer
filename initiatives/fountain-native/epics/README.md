# fountain-native — epics (execution order)

1. **io** — open and save Fountain as the native format (done 2026-10-26:
   1 done 2026-10-24; 3, remove `.trelby`, and 4, tests off `.trelby`, done
   2026-10-25; 2, per-script settings, moved to the `settings` epic on
   2026-10-26; 5, one Fountain reader and writer, done 2026-10-26; task
   files removed 2026-10-28, history: git log --
   initiatives/fountain-native/epics/io)
2. **scenes** — permanent scene numbers, letters for inserts (6 tasks, all
   done: 1–4 and 6 on 2026-10-27, 5, records follow moved and renumbered
   scenes, on 2026-10-30; task files removed, history: git log --
   initiatives/fountain-native/epics/scenes)
3. **notes** — annotations on spans, elements and scenes, outside the
   Fountain text (1 task, done 2026-10-30; history: git log --
   initiatives/fountain-native/epics/notes)
4. **settings** — per-script settings as a record in the film root (1 task,
   was io/2, done 2026-10-30; history: git log --
   initiatives/fountain-native/epics/settings)

5. **import** — future features for Import → Fountain (1 task: the old
   importer's options; not scheduled, not part of the initiative gate)

`scenes`, `notes`, `settings` and `import` need `io`. Cross-repository: `scenes` keeps
mocap-previz `fountain-input/2` ("scene number as the scene identity") true.
