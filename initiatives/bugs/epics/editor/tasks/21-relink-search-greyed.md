## 21. The Missing files dialog lists a problem it can't act on

- **Status:** Fixed (2026-10-31) — fixes/0000af/film-notices
- **Symptom:** On Open film, the Missing files dialog lists "Script
  settings — The title page was edited outside the writer…", and Search
  and Skip stay greyed out for it, with nothing saying why or what to do.
- **Where:** every film problem goes into that one dialog (`openFilm`,
  `trelby/trelbyframe.py:794`); Search and Skip are enabled only for a
  problem with a file to look for (`p.ref`, `updateButtons`,
  `trelby/relinkdlg.py:100-103`); the title-page notice has none: no file
  is missing, the settings record's title layout no longer matches the
  script's Fountain title block (`scriptsettings.apply`,
  `trelby/scriptsettings.py:285-290`, listed by `loadFor`,
  `trelby/scriptsettings.py:345`).
- **Reproduce:** a film whose `script.fountain` was replaced or its title
  page edited in another program; Open film (Rafael, 2026-10-31).
- **Impact:** confusing: it looks like a file to find. The notice itself
  is right (the title page opens from the Fountain text, default layout)
  and, by reading the code, goes away after the script is saved once,
  since the save records the current title block (`saveFor`).
- **Likely fix:** show problems with nothing to search for as notices
  (no greyed buttons, or a line saying no action is needed), and the
  dialog's title not "Missing files" when there are only notices.
