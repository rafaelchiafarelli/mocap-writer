## 1. pt-BR dictionary: licence and how to read it

- **Type:** study (measurements in a throwaway container; nothing in
  `trelby/`, nothing added to the image yet)
- **Depends on:** —
- **Why:** the checker (`trelby/spellcheck.py`) reads one plain list of
  lower-case words, `trelby/dict_en.dat` (175 365 words, about 1.8 MB),
  into a set, plus a dict keyed by each word's first two letters for
  suggestions (`spellcheck.loadDict`, `trelby/spellcheck.py:15-45`;
  suggestions `trelby/spellcheckdlg.py:180-200`). Words are split with
  `str.isalnum`, so accents are already handled
  (`util.splitToWords`, `trelby/util.py:599-630`); the file name is
  hard-coded. Portuguese dictionaries come as Hunspell `.dic` + `.aff`
  files (stems plus rules for plurals, genders and verb forms), not as a
  plain list.
- **Contract:**
  - In: the pt-BR Hunspell dictionary (VERO, as packaged by Ubuntu 24.04:
    `hunspell-pt-br`), and a sample of real pt-BR script text (neutral
    text, not film material: e.g. `tests/fixtures/fountain/sample_ptbr.fountain`
    plus a longer neutral text)
  - Requires:
    - **Licence:** the exact licence of the dictionary files (from the
      package's `copyright` file and VERO's own notice), checked against
      the Mocap Studio rule (commercial use; the weights'/asset's licence,
      not only the code's). If it is not on the rule's list (MIT,
      Apache-2.0, BSD, CC0, CC-BY; GPL-family for tools), it goes to
      Rafael with the facts; look for an alternative pt-BR list too.
    - **Option 1, flat list:** expand the dictionary with Hunspell's
      `unmunch` (or `wordforms`) into one word per line, like
      `dict_en.dat`. Measure: number of words, file size, time and memory
      for `loadDict` to load it, suggestion time for a misspelled word.
    - **Option 2, Hunspell engine:** check words and get suggestions
      through a library that reads `.dic`/`.aff` directly (`spylls`, pure
      Python; or `pyenchant` / a Hunspell binding over the system
      `libhunspell`). For each candidate: licence, whether it is packaged
      for the image (apt or the hashed lockfile, `DEPENDENCIES.md`), load
      time, check and suggestion time, memory.
    - **Quality:** on the sample text, how many correct words each option
      flags (false alarms; conjugated verbs and plurals especially) and
      whether the suggestions for a few typos are the right word.
  - Delivers: a table of the two options (licence, size, load time,
    memory, speed, false alarms, suggestion quality) and a recommendation;
    Rafael decides. The decision is written here.
- **Pre-work:** —
- **Out of scope:** changing `trelby/`; adding anything to the image or
  the lockfile (pt-br/1 does that once decided).
- **Tests:** none (a study); the measurements are reproducible from the
  commands written in this file.
