# fountain-native — epics (execution order)

1. **io** — open and save Fountain as the native format (4 tasks: 1 done
   2026-10-24; 2, per-script settings, on hold for the file-format
   investigation; 3, remove `.trelby`, done 2026-10-25; 4, tests off
   `.trelby`, done 2026-10-25)
2. **scenes** — permanent scene numbers, letters for inserts (1 task; decided
   2026-10-25, a few open points left)
3. **notes** — notes on spans of text (1 task, waits for its format decision)

`scenes` and `notes` need `io`. Cross-repository: `scenes` keeps
mocap-previz `fountain-input/2` ("scene number as the scene identity") true.
