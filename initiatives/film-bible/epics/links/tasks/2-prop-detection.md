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
    Punctuation ends a run (`XÍCARA.`); a one-letter capital word sits
    inside a run like any other: `CAIXA DE FÓSFORO` and `CAIXA E VELA` are
    one prop each, `CAIXA de FÓSFORO` and `CAIXA e VELA` are two (Rafael,
    2026-10-25);
  - a run that is not a known character and not a known prop is
    offered as a new prop (state `script-stated`); a known prop links to the
    scene number; nothing is created without the creator's confirmation; a word
    can be marked "not a prop" once for the whole film
  - Delivers: the suggestion list and the links
- **Pre-work:** —
- **Out of scope:** AI classification
- **Tests:** a multi-word run is one prop; punctuation ends it; one-letter
  capitals inside a run, lower-case words split it; a run at the end of what is being
  typed is not offered yet; character names skipped; plural and accents;
  "not a prop" remembered
