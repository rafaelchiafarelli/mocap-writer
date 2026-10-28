# file-format — mocap-writer

**Status:** In progress — study done (2026-10-25); layout planned.

**Decided (Rafael, 2026-10-25):** **option A**, a folder of Harpia JSON
records with ISOXML's architecture: a root index (`film.json`), flat
records with typed stable ids linked by id only, one owner per part,
binaries beside the records, strict validation on read. **Keep C in
mind**, a change log in SQLite, for scale and team sync later: A is built
so that moving to C is a migration, not a redesign
(study/3, options; history: git log -- initiatives/file-format/epics/study).

**Decided (Rafael, 2026-10-25): opening a film never breaks.** A file that
is missing or moved is reported with a warning, the rest of the film
opens, and the creator can search for the file; the location found tells
the writer where the other missing files probably are (`layout/3`).

**Goal:** choose the format the writer keeps a film in: one design that holds
the script and everything around it, instead of a Fountain file plus loose
sidecars.

**Why now:** `.trelby` is gone (fountain-native/io/3), the sidecar for
per-script settings is on hold (fountain-native/io/2), and film-bible,
preprod-link and story-structure each plan their own files. Rafael wants one
format that can hold all of it before more of it is built.

**Scope:** the study (what the format must hold, candidates, decision);
then the layout every part uses: the root index, the id scheme, history.

**Out of scope:** the contents of each part (film-bible, preprod-link and
fountain-native tasks); building option C; the capture pipeline's own
files (`session.json`, `mocap_data.json`, ...), except as touchpoints.

**Decisions the study weighed** (outcome in study/3, options, in git history):
- film-bible: "the maps are **folders in the film root**
  (`<film-root>/bible/`), with their format defined as a Harpia contract"
  (2026-10-23);
- fountain-native/io/2: "a sidecar file next to the script" (2026-10-25,
  replaced by a settings record in the film root, see the decision);
- preprod-link: "the link goes through files in the film root whose format
  is a Harpia contract" (2026-10-24).

**Initiative gate:** Rafael picks a format (done 2026-10-25, A); the tasks
that change because of it are re-planned (done 2026-10-25: film-bible
contract/2, fountain-native io/2, preprod-link contract/1); `layout/1`
works on the neutral sample and Rafael decides `layout/2`.

Epics: `epics/README.md`.
