## 2. The bible review

- **Status:** Done (2026-10-31) — `importfilm.plan` / `apply`, `trelby/biblereviewdlg.py`, opened at the end of Import into film, on Import → Into this film (no scenes), and from From script → Review all…; checked through the real window.
- **Type:** code
- **Depends on:** 1; film-bible/links/1, 2 and 5 (`setPlan`,
  `propPlan`, `characterPlan`); Rafael's decisions 1 and 2
  (`../../../import-to-film.md`: new items ticked, named as written)
- **Contract:**
  - In: the film made by task 1 (or any open film, from the bible
    panel)
  - Requires: one dialog with three sections (sets, characters, props),
    each line a new item with its scenes or a link to a known one, ticked
    as decided; Create applies all of it in one go; the props the creator
    unticks can be marked "not a prop" from the same dialog; nothing is
    written before Create
  - Delivers: the review dialog, opened at the end of Import into film
    and from From script → Review all
- **Pre-work:** none (decisions taken 2026-10-31)
- **Out of scope:** wardrobe (it has no source in the script; task 3
  reports the gaps)
- **Tests:** the combined plan of a neutral script; Create makes exactly
  the ticked items and links; Cancel writes nothing
