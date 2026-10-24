## 2. Prop detection

- **Type:** code
- **Depends on:** maps/3; editor-ux/typing/2 (`find_prop_words`)
- **Contract:**
  - In: capitalized words in Action lines
  - Requires: a word that is not a known character and not a known prop is
    offered as a new prop (state `script-stated`); a known prop links to the
    scene id; nothing is created without the creator's confirmation; a word
    can be marked "not a prop" once for the whole film
  - Delivers: the suggestion list and the links
- **Pre-work:** —
- **Out of scope:** AI classification
- **Tests:** character names skipped; plural and accents; "not a prop" remembered
