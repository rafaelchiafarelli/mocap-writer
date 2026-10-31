# import-to-film — mocap-writer

**Status:** Planned (2026-10-28); decisions taken 2026-10-31. Asked by Rafael, 2026-10-28: "complete
process the Fountain when we import it".

**Goal:** importing a script (PDF, Final Draft, Fountain...) ends in a
complete film, not a lone tab: the film root made, the script saved as
its Fountain with every scene numbered, and the bible offered from the
script (sets, characters, props and their scenes) in one review, so the
creator goes from a PDF to a film with a bible in one pass.

**Why:** today the same result takes Import, New film, then four separate
From script commands (film-bible/links), each with its own checklist.

**Scope:** one command from a file to a film; one review of everything the
script offers to the bible; a report of what was made and what still
needs the creator.

**Out of scope:** the importers themselves (pdf-import, done); annotations
(fountain-native/notes/1); the preprod-link sync; AI filling the fields
(mocap-preprod agents).

**Decided (Rafael, 2026-10-31):**
1. In the import's review, new sets, characters and props are **ticked
   by default** (a new film has nothing yet; the creator unticks).
2. New items are named **as the script writes them** (`SALA DE JANTAR`),
   as From script does.
3. File → Import with a film open offers both: import **into this film**
   (the script replaces nothing: it opens in a tab, and the review adds to
   this film's bible) or **into a new folder** (a new film, as Import into
   film). Into a new folder, the **original file is copied** into the
   film, `<film-root>/source/<file name>`, next to the `script.fountain`
   made from it.

**Initiative gate:** a real script's PDF becomes a film with its bible in
one pass (a film session, Rafael's call), and opens again with no problems.

Epics: `epics/README.md`.
