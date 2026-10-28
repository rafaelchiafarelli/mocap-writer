## 16. Quadruple click does not select the element

- **Status:** Fixed (2026-10-28) — fixes/00009f/multi-click — Rafael (2026-10-28): three clicks select the element, so this is fixed with editor/15
- **Symptom:** A fourth click does not select the whole element (the whole Action, Dialogue, Character...).
- **Where:** no multi-click handling (`trelby/trelbyctrl.py:633`); `Screenplay.getElemIndexesFromLine` (`trelby/screenplay.py:1079`) gives an element's first and last line.
- **Reproduce:** click four times in a Dialogue element.
- **Impact:** missing editing gesture (Rafael, 2026-10-24: counted as a bug; wanted, not now).
- **Likely fix:** the same click counter as editor/15; on the fourth, mark from the element's first line to the end of its last.
