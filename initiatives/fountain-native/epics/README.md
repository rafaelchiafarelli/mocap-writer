# fountain-native — epics (execution order)

1. **io** — open and save Fountain as the native format (1 task)
2. **scenes** — permanent scene numbers, letters for inserts (1 task; decided
   2026-10-25, open points answered 2026-10-26: ready to implement)
3. **notes** — notes on spans of text (1 task, waits for its format decision)

`scenes` and `notes` need `io`. Cross-repository: `scenes` keeps
mocap-previz `fountain-input/2` ("scene number as the scene identity") true.
