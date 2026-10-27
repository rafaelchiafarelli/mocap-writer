## 2. Act panel

- **Type:** code
- **Depends on:** 1 (the act break is the marker)
- **Decided (Rafael, 2026-10-26):** a **panel on the right** of the
  editor shows the acts and their sizes; **zoom does not affect it and
  scrolling does not move it**; sizes are counted **in scenes**; the act
  the cursor is in is highlighted. The feature grows later.
- **Contract:**
  - In: the script being edited (its Act break and Scene elements) and
    the cursor line
  - Requires:
    - a function without wx, `acts.actsOf(sp) -> [Act]`: one `Act` per
      Act break element, in order, with its name (the element's text, or
      `Act n` when empty), its first line and its number of scenes (Scene
      elements from it up to the next act break); scenes before the first
      act break form an unnamed first part, listed only if it has scenes;
      `acts.actAt(acts, line)` gives the act holding a line;
    - the panel, one per script tab, right of the scroll bar, fixed width:
      one row per act, its name, a bar whose length is its scene count
      against the largest act, and `n scenes`; the cursor's act
      highlighted; a hint when the script has no act break;
    - drawn with a font of its own, not the editor's zoomed one; painted
      with the theme's colors and repainted when the theme changes;
    - refreshed when the script or the cursor's act changes, not on every
      keystroke that changes neither
  - Delivers: `trelby/acts.py`, the panel, its place in the tab
- **Pre-work:** —
- **Out of scope:** click to jump to an act; hiding the panel; pages per
  act; structure models and beats (study/1)
- **Tests:** `actsOf` on a script with no act break, with acts, with
  scenes before the first act, with an empty act name, with an act with
  no scenes; `actAt` before, on and after a marker
