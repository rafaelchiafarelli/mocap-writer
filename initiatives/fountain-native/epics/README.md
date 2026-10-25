# fountain-native — epics (execution order)

1. **io** — open and save Fountain as the native format (2 tasks: 1 done
   2026-10-24; 2, per-script settings in a sidecar file, decided 2026-10-25)
2. **scenes** — permanent scene numbers, letters for inserts (1 task; decided
   2026-10-25, a few open points left)
3. **notes** — notes on spans of text (1 task, waits for its format decision)

`scenes` and `notes` need `io`. Cross-repository: `scenes` keeps
mocap-previz `fountain-input/2` ("scene number as the scene identity") true.
