## 4. Open film, New film

- **Type:** code
- **Depends on:** layout/1
- **Decision (Rafael, 2026-10-28):** opening a film is explicit: File →
  Open film… picks a folder, File → New film… makes one. A `.fountain`
  opened on its own never loads the film around it.
- **Contract:**
  - In: a folder chosen in a dialog
  - Requires: **Open film…** opens `film.json` with layout/1; the
    `script` part opens in a tab and the film's other parts are available
    to the panels that use them (film-bible tree); a missing or invalid
    `film.json` is a message, never a crash; the problems layout/1 lists
    are shown (layout/3 turns them into the search); **New film…** takes
    an empty folder (or one with no `film.json`) and writes `film.json`
    with the default parts and the `w` space; when the current tab holds
    a script, it is saved as the film's `script.fountain`; the title bar
    names the film
  - Delivers: the two menu commands and the open film the panels read
- **Pre-work:** —
- **Out of scope:** search for missing files (layout/3); recent films list
- **Tests:** new film → valid `film.json` and the script inside; open
  film → script tab opened; no `film.json` → message
