# import-to-film — mocap-writer

**Status:** Planned (2026-10-28). Asked by Rafael, 2026-10-28: "complete
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

**Open decisions for Rafael:**
1. In the import's review, are new sets, characters and props **ticked by
   default** (a new film has nothing yet, so unticked means ticking them
   all), or unticked as in From script (never made silently)?
2. Names of new items: **as the script writes them** (`SALA DE JANTAR`,
   as From script does today) or capitalized (`Sala de Jantar`)?
3. Does the import also run on File → Import when a film is already open
   (adding to that film's bible), or only through the new command?

**Initiative gate:** a real script's PDF becomes a film with its bible in
one pass (a film session, Rafael's call), and opens again with no problems.

Epics: `epics/README.md`.
