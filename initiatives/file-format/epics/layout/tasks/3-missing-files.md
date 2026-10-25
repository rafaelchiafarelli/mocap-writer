## 3. Missing files: warn and search

- **Type:** code
- **Depends on:** layout/1 (the list of problems on open)
- **Decision (Rafael, 2026-10-25):** the opener must not break. If it does
  not find the files, a warning lets the creator search for them, and the
  location found gives the pattern of where the files are stored.
- **Contract:**
  - In: the list of problems layout/1 returns when a film opens
  - Requires: one warning for all missing files (not one per file),
    listing what is missing and where it was expected; the film is already
    open and usable behind it; for each missing file the creator can
    **search** (a file dialog) or **skip** (stays listed as missing, asked
    again on the next open); a file found somewhere else gives the
    **pattern** (the part of the path that changed, e.g. a film moved from
    one drive or folder to another), which is tried on every other missing
    file, and the ones it finds are shown for the creator to accept, never
    applied silently; what was accepted is saved where the reference lives
    (the part's path in `film.json`, or the file's path in its record), so
    the next open finds it; a found file must be the expected kind (a
    `.fountain` for the script, an image for a photo...), otherwise the
    creator is told and it is not linked
  - Delivers: the warning dialog and the relink library
- **Pre-work:** a neutral film root fixture with parts and media to move
  and delete in tests
- **Out of scope:** searching whole disks on its own (the creator points
  to the place); missing `film.json` (layout/1 stops the open with a
  message)
- **Tests:** a moved film root: one file found → the pattern finds the
  rest, the creator accepts, the next open has no problems; skip keeps the
  file listed; a file of the wrong kind is refused; nothing changes on
  disk until the creator accepts
