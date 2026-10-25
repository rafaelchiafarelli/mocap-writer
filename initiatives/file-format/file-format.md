# file-format — mocap-writer

**Status:** Planned — not started. A study first (Rafael, 2026-10-25).

**Goal:** choose the format the writer keeps a film in: one design that holds
the script and everything around it, instead of a Fountain file plus loose
sidecars.

**Why now:** `.trelby` is gone (fountain-native/io/3), the sidecar for
per-script settings is on hold (fountain-native/io/2), and film-bible,
preprod-link and story-structure each plan their own files. Rafael wants one
format that can hold all of it before more of it is built.

**Scope:** what the format must hold (task 1), the candidate formats and how
they score (task 2), options and a recommendation for Rafael (task 3).

**Out of scope:** code, until Rafael decides; the capture pipeline's own
files (`session.json`, `mocap_data.json`, ...), except as touchpoints.

**Decisions this study may revisit** (Rafael's call, nothing changes until he
decides):
- film-bible: "the maps are **folders in the film root**
  (`<film-root>/bible/`), with their format defined as a Harpia contract"
  (2026-10-23);
- fountain-native/io/2: "a sidecar file next to the script" (2026-10-25,
  now on hold);
- preprod-link: "the link goes through files in the film root whose format
  is a Harpia contract" (2026-10-24).

**Initiative gate:** Rafael picks a format; the tasks that change because of
it (film-bible contract/2, fountain-native io/2, preprod-link contract/1 and
2) are re-planned.

Epics: `epics/README.md`.
