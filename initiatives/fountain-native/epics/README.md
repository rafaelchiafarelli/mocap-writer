# fountain-native — epics (execution order)

1. **io** — open and save Fountain as the native format (1 task)
2. **scenes** — scene ids and automatic numbering (1 task, **waits for Rafael's decision**)
3. **notes** — notes on spans of text (1 task, waits for its format decision)

`scenes` and `notes` need `io`. Cross-repository: what `scenes` decides changes
mocap-previz `fountain-input/2` ("scene number as the scene identity").
