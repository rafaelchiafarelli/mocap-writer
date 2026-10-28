## 14. Double click does not select the word

- **Status:** Fixed (2026-10-28) — fixes/00009f/multi-click
- **Symptom:** A double click only moves the cursor; in current text editors it selects the word under the pointer.
- **Where:** `EVT_LEFT_DCLICK` is bound to the single-click handler `OnLeftDown` (`trelby/trelbyctrl.py:66`, `trelby/trelbyctrl.py:633`). `Screenplay.getWord(line, col)` (`trelby/screenplay.py:1646`) and `setMark` (`trelby/screenplay.py:2441`) exist.
- **Reproduce:** double-click a word in the script.
- **Impact:** missing standard editing gesture (Rafael, 2026-10-24: counted as a bug; wanted, not now).
- **Likely fix:** a double-click handler that marks the word's start and puts the cursor at its end.
