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

## Results (2026-10-27)

**Status:** Done (2026-10-27) — decided, see "Decision".

Material in [`1-dictionary-study/`](1-dictionary-study/): `run.sh`
reproduces everything (run from the repository root after
`docker/test.sh` has built `mocap-writer:dev`; a throwaway container,
removed at the end), `measure.py` does the load/check/suggest
measurements, `sample_long_ptbr.txt` is the longer neutral text (written
for this study, about 500 words of scene text with conjugated verbs,
plurals, accents and a clitic). Together with
`tests/fixtures/fountain/sample_ptbr.fountain`: 548 words, 354 distinct.
Twelve typos with the word meant are listed in `measure.py` (`TYPOS`).
Machine: the processing PC (`DEPENDENCIES.md`); the table is from the
first run, a second run with `run.sh` matched it within a few percent
except where marked.

### Licence (goes to Rafael)

- **Dictionary files** (`pt_BR.dic`/`.aff`, VERO 3.2 by Raimundo Santos
  Moura, Ubuntu 24.04 `hunspell-pt-br 1:24.2.1-1` from
  libreoffice-dictionaries): Debian's `copyright` says
  `Files: dictionaries/pt_BR/*` — `License: LGPL-3 or MPL`; VERO's own
  notice (`pt_BR.aff`, header) says "LGPLv3 … e pela Mozilla Public
  License" (version not given in either). **Not on the rule's list**
  (MIT, Apache-2.0, BSD, CC0, CC-BY): it is weak copyleft on a data file.
  Both licences allow commercial use and selling; the obligation is to
  ship the files' source (they *are* their source) and to publish changes
  made to those files under the same licence. Using it unmodified, read
  from `/usr/share/hunspell/`, adds no obligation on Trelby's own code
  (already GPL-2.0).
- **Alternative pt-BR lists:** none found under a permissive licence.
  The other known one, br.ispell (Ricardo Ueda Karpischek; Debian
  `wbrazilian`), is GPL; LanguageTool and `dictionary-pt` (npm) both
  redistribute VERO under LGPL-3/MPL.
- **Engines:** `libhunspell` MPL-1.1/GPL-2.0/LGPL-2.1 (tri-licence;
  a tool, GPL-family); `libenchant-2-2` LGPL-2.1+; `pyenchant` 3.3.0
  LGPL-2.1; `python3-hunspell` (pyhunspell) LGPL-3+; `spylls` 0.1.7 —
  its wheel's `LICENSE` file is MPL-2.0 while its metadata classifier
  says MIT (the file is what counts). LGPL is GPL-family; MPL is not on
  the list either.

### Options measured

| | Flat list, full (1) | Flat list, no prefixes (1b) | Hunspell via pyenchant (2a) | spylls (2b) |
|---|---|---|---|---|
| How | `unmunch`, lower-cased, hyphenated forms dropped | same, `PFX` rules removed | `enchant.Dict("pt_BR")` → libhunspell | pure-Python Hunspell |
| Words / size | 16 868 563 words, 267 MB (44 MB gz) | 2 199 362 words, 29 MB (5.7 MB gz) | `.dic` 4.5 MB + `.aff` 1.0 MB (package 9.6 MB installed) | same files |
| Load | 6.96 s | 0.69 s | 0.12–0.15 s | 1.45 s |
| Memory (RSS added) | +2 340 MB | +331 MB | +37 MB | +267 MB |
| Check | ≈1 µs/word | ≈1 µs/word | 6–7 µs/word | 100 µs/word |
| False alarms on the samples¹ | 1 (`Nós`) | 5 (`Nós amanhã anuncia atrás descarregar`) | 0 | 0 |
| Suggestions: meant word in top 5 | 7–9/12² | 7–10/12² | **12/12** | 12/12 |
| Suggestion time (avg / worst) | 1.3 s / 10.8 s | 145 ms / 953 ms | **34 ms / 105 ms** | 7.9 s / 86 s |
| Packaging | a generated file in the repo or built in the image | same | apt `hunspell-pt-br libenchant-2-2` (+ `libhunspell`, `hunspell-en-us` as deps) + `pyenchant==3.3.0` pure-Python wheel in the hashed lockfile | apt `hunspell-pt-br` + `spylls` wheel |

¹ Not counting the Fountain/English words (`Title Author EXT INT
prop`), which each option flags in part.
² Two runs gave different counts: Trelby's loop walks a Python `set`,
whose order changes from run to run (string hash randomisation), and its
five-word FIFO keeps whichever ties it meets last. English `dict_en.dat` on the
same samples, for reference: 288 unknown, 1/12 suggestions, 0.05 s and
+25 MB to load.

Measured with Trelby's own code for the flat lists (`spellcheck.loadDict`
and `lev`, the suggestion loop of `SpellCheckDlg.OnSuggest` copied without
the user dictionaries). `python3-hunspell` (pyhunspell over the same
library) gives the same answers and times as pyenchant (0.13 s, +37 MB,
34 ms), but PyPI has no wheel for it (it would need a compiler in the
image), so it is not a candidate for the lockfile.

### Findings

- **`unmunch` loses real words.** The expansion is 83 189 912 lines
  (1.47 GB) in 5.6 s; 66 M of them have a hyphen (enclitics like
  `desaferrarem-nos`), which Trelby can never look up because it splits
  words at `-`. But it still misses forms Hunspell accepts: `nós`
  (`nó/B…`, `SFX B 0 s [^ã][…ó…]`: the two-character condition is not
  applied the way libhunspell does). How many words are lost in total is
  unknown, only that it happens.
- **The `PFX` rules are not optional.** They carry the productive
  prefixes (`neo`, `ultra`, `supra`, `macro`, …) but also `des-` and
  `a-` (`descarregar` = `des` + `carregar`, `amanhã`, `atrás`), so
  dropping them to shrink the list loses common words.
- **Trelby's suggestion loop does not scale to Portuguese.** It keeps the
  last five words at the lowest distance seen so far among the words
  sharing the first two letters, so with millions of forms it returns
  near neighbours in hash order (`caza` → `cava capa caía caia cara`,
  no `casa`, and a different five on the next run) and is slow (`conseguiriamos`: 10.8 s). Hunspell's own
  suggester uses the `.aff` `TRY`/`MAP`/`REP` tables (`aáãâ`, `cç`,
  …), which is why it finds `você`, `não`, `exceção`.
- Case: Hunspell checks the word as written (it accepts `JOÃO`,
  `MANHÃ`, `Você`); the flat lists are checked lower-cased, as now.
- English stays available either way: option 2 can open `en_US` too
  (`hunspell-en-us` comes in as a dependency of `libenchant-2-2`), or
  keep `dict_en.dat` for English.

### Recommendation

**Option 2a: Hunspell through `pyenchant`**, with the system
`hunspell-pt-br` dictionary read in place (not copied into the repo):
no false alarms on the samples, every typo's meant word among the
suggestions, 0.15 s and +37 MB to load, 34 ms per suggestion, and it
packages as the stack wants (apt for the C library and the dictionary,
one pure-Python wheel in the hashed lockfile). A flat list is either
huge (2.3 GB of memory) or wrong (missing `amanhã`, `atrás`), and in both
cases Trelby's suggestions are poor. spylls gives the same answers but is
far too slow to suggest.

### Decision (Rafael, 2026-10-27)

- **Licence:** VERO's `pt_BR.dic`/`.aff` (LGPL-3 or MPL) are accepted,
  used unmodified, read from the system package. spylls (MPL-2.0) was
  accepted too, but is not used. `libenchant` / `pyenchant` (LGPL-2.1)
  are GPL-family libraries.
- **Option: 2a, Hunspell through `pyenchant`.** Rafael first picked
  spylls, then chose pyenchant once told spylls takes 7.6 s per
  suggestion on average (worst 86 s).
- For pt-br/1: apt `hunspell-pt-br` and `libenchant-2-2` in the
  Dockerfile, `pyenchant==3.3.0` in the hashed lockfile.
