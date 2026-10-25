## 15. Triple click does not select the line

- **Status:** Open
- **Symptom:** A triple click does nothing more than a single click; in current text editors it selects the line.
- **Where:** no multi-click handling: `OnLeftDown` (`trelby/trelbyctrl.py:531`) handles every click the same; wx reports no triple click, so clicks must be counted by time and position.
- **Reproduce:** triple-click a line of Action.
- **Impact:** missing standard editing gesture (Rafael, 2026-10-24: counted as a bug; wanted, not now).
- **Likely fix:** count clicks; on the third, select the line. To decide when fixing: the screen line (a wrapped `Line`) or the paragraph up to a forced line break (`getParaFirstIndexFromLine`, `trelby/screenplay.py:1344`).
