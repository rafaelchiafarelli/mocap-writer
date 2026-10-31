## 1. The record and its form

- **Type:** code
- **Depends on:** contract/1
- **Contract:**
  - In: the open film
  - Requires: `trelby/frontmatter.py` (no wx): `load(film)` → the record
    or an empty one (a missing file is no problem, an invalid one is a
    film problem), `save(film, record)` through `Film.writeText` (logged);
    the bible panel shows a **Front matter** node above the maps; selecting
    it shows a form: the title page fields (co-authors one per line), the
    overview's Include and what it lists, the pitch's Include and three
    texts, the argument's Include and its text (multi-line); a value is
    saved when its control loses the focus, as the bible form does
  - Delivers: the module, the node and form, tests, the as-built
- **Pre-work:** none
- **Tests:** load of a film without the file; save → load round trip;
  an invalid file is a problem, not a crash; the change log has the write
