## 14. Double click does not select the word

- **Status:** Open
- **Symptom:** A double click only moves the cursor; in current text editors it selects the word under the pointer.
- **Where:** `EVT_LEFT_DCLICK` is bound to the single-click handler `OnLeftDown` (`trelby/trelbyctrl.py:64`, `trelby/trelbyctrl.py:485`). `Screenplay.getWord(line, col)` (`trelby/screenplay.py:1978`) and `setMark` (`trelby/screenplay.py:2764`) exist.
- **Reproduce:** double-click a word in the script.
- **Impact:** missing standard editing gesture (Rafael, 2026-10-24: counted as a bug; wanted, not now).
- **Likely fix:** a double-click handler that marks the word's start and puts the cursor at its end.
