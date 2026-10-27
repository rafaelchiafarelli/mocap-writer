## 3. Affected records

- **Type:** code
- **Depends on:** sync/1, sync/2; film-bible/links
- **Contract:**
  - In: a change set and `<film-root>/bible/`
  - Requires: each change is mapped to the bible records whose values cite
    that scene as their source (set, characters, props, wardrobe); those
    values are listed as **needs review** in the change panel; a value whose
    source scene did not change is never listed; no state is changed
    automatically — whether "needs review" becomes a stored state is decided
    with Rafael during this task's planning
  - Delivers: the affected-records list and its section in the change panel
- **Pre-work:** Rafael's decision above
- **Out of scope:** editing records (the maps' editors, review/1)
- **Tests:** renamed character → its records listed; removed scene → values
  sourced from it listed; untouched scene → nothing listed
