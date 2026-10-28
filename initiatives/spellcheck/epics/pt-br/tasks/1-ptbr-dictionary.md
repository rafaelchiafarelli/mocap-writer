## 1. The spell checker in pt-BR

- **Type:** code (and the Docker image)
- **Depends on:** study/1 (Rafael's decision on the dictionary and on
  option 1 or 2)
- **Contract:**
  - In: the dictionary and engine chosen in study/1
  - Requires:
    - the pt-BR dictionary is installed in the Docker image (apt, or
      generated at image build), never committed to git unless study/1
      decides a flat list is small enough and its licence allows it; its
      licence is recorded in `docker/CLAUDE.md`
    - a global setting **dictionary language**, `en` or `pt-BR`, in
      `ConfigGlobal` (saved in the config, shown on the Misc settings
      page); default `en` for an existing config. Nothing is guessed from
      the script's text
    - Tools → Spell checker uses that language's dictionary for "is this
      word known" and for suggestions; the script dictionary, the global
      dictionary and character names keep working as now, in either
      language
    - if the chosen dictionary is missing (e.g. outside the Docker image),
      a message says which one and how to get it; the checker does not
      crash
  - Delivers: `spellcheck` able to load either language; the setting; the
    image with the pt-BR dictionary
- **Pre-work:** study/1 decided
- **Out of scope:** checking while typing; a per-script language (after
  fountain-native/settings/1); other languages
- **Tests:** a correct pt-BR sentence with accents, plurals and conjugated
  verbs has no unknown word; a misspelled word is found and its
  suggestions include the right word; switching the setting back to `en`
  gives the English behaviour; a missing dictionary gives the message,
  not a crash; the setting round-trips through the config file
