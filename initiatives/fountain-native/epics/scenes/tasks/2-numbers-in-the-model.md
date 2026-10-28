## 2. The number lives in the script model and the file

- **Status:** Done (2026-10-27)

- **Type:** code
- **Depends on:** 1 (the rule's `parse` and `check`)
- **Contract:**
  - In: a `.fountain` with or without `#n#` on its scene headings; every
    editing command
  - Requires:
    - `Line` gets `num` (`""` by default): the scene number, kept on the
      first line of a Scene element; it is in `str(line)` / `fromStr`, in
      `==`, and in every copy of a line the model makes (`__deepcopy__`,
      undo), so undo and redo give the number back;
    - wrapping keeps it on the element's first line; splitting a heading
      (Enter) keeps it on the first part, as Trelby keeps the element's
      type there (implemented 2026-10-27; pasting several elements at the
      start of a heading leaves it with the heading's text); joining a heading
      into the element before drops it (that scene is gone); changing a
      heading's type keeps it on the line, so changing back restores it;
      copy and cut never put it on the clipboard (a pasted scene is new);
    - `fountain.load` puts a heading's `#n#` into `num` (the text stays
      without it, as now); `fountain.generate` writes `num` as `#n#`,
      keeping the original spacing when the number did not change, and an
      element whose number changed counts as edited;
    - after open, `scenenumbers.check` problems are reported to the user
      (duplicates, order, other forms, scenes with no number), never
      fixed (also: PDF import puts its numbers on `num`, not in the
      text, so they read back the same).
  - Delivers: `line.py`, `screenplay.py`, `undo.py`, `fountain.py`
    changes; the report on open (`trelbyctrl.py`)
- **Pre-work:** —
- **Out of scope:** giving numbers (task 3); showing them (task 4)
- **Tests:** numbers survive open → save → open byte-identical; a number
  read into `num`; edited heading keeps its number; changed number written;
  undo/redo of typing, split, join, cut, paste and type change keep the
  numbers right; cut/copy carry no number; `check` on open
