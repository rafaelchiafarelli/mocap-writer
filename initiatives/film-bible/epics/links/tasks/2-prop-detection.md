## 2. Prop detection

- **Type:** code
- **Depends on:** maps/3; editor-ux/typing/2 (`find_prop_words`)
- **Contract:**
  - In: runs of capitalized words in Action lines
  - Requires: **a prop is a run of consecutive fully capitalized words**
    (`XÍCARA AZUL` is one prop, not two); the run ends at the first word that
    is not fully capitalized, and only then is it offered, so a run still
    being typed is never offered half-written (Rafael, 2026-10-25). This
    changes `find_prop_words`, which today returns each word on its own
    (`trelby/propwords.py:15`), and the editor's underline with it.
    To confirm with Rafael: whether punctuation (`XÍCARA.`) and the end of
    the element also end a run; whether a one-letter capital word (`A`,
    `O`, `E`) can sit inside a run (`CAIXA DE FÓSFORO` vs `CAIXA E VELA`);
  - a run that is not a known character and not a known prop is
    offered as a new prop (state `script-stated`); a known prop links to the
    scene id; nothing is created without the creator's confirmation; a word
    can be marked "not a prop" once for the whole film
  - Delivers: the suggestion list and the links
- **Pre-work:** —
- **Out of scope:** AI classification
- **Tests:** a multi-word run is one prop; a run at the end of what is being
  typed is not offered yet; character names skipped; plural and accents;
  "not a prop" remembered
