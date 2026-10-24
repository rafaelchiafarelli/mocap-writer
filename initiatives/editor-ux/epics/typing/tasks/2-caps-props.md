## 2. Capitalized words in Action lines

- **Type:** code
- **Depends on:** —
- **Contract:**
  - In: an Action line
  - Requires: a word of 2+ letters written fully in capitals (accents
    included: `CADEIRA`, `LÂMPADA`) is drawn underlined; display only, the
    text is not changed; the detection is one function that `film-bible`
    reuses to create prop records
  - Delivers: the underline and `find_prop_words(line) -> list[(start, end, word)]`
- **Pre-work:** —
- **Out of scope:** creating prop records (film-bible/links); character names
  in Action (also in caps by convention: telling them apart is film-bible's
  job, using the character map)
- **Tests:** accents; one-letter words and `I`/`A` ignored; punctuation
  around the word; a line that is all caps
