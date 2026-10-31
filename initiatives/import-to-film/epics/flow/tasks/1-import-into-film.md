## 1. Import into film

- **Type:** code
- **Depends on:** file-format/layout/4 (New film); the importers
  (`MyCtrl.importFile`)
- **Contract:**
  - In: a file to import and a folder for the film (empty, or with no
    `film.json`)
  - Requires: File → Import into film… asks for both; the file is
    imported as File → Import does (the PDF importer's report and
    `IMPORT:` notes kept); the film is made as New film does and the
    script saved as its `script.fountain`, which numbers every scene; if
    the import fails or is cancelled, no film is made; if the save cannot
    number the scenes, the film is made and the creator is told, as New
    film does; the original file is copied to `<film-root>/source/<file
    name>` (decision 3; `source/` is a folder part `source` added to a new
    film's parts); with a film open, File → Import asks "Into this film" /
    "Into a new folder" / "Just open it" (decision 3)
  - Delivers: the command; the open film with its script
- **Pre-work:** a neutral PDF fixture already exists for pdf-import
  (`tests/fixtures/`); a neutral `.fountain` too
- **Out of scope:** the bible (task 2)
- **Tests:** import of a neutral `.fountain` and a neutral PDF into a new
  folder → a film that opens with no problems and numbered scenes; a
  cancelled import makes nothing; the original is in `source/`
