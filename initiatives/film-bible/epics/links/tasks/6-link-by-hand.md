## 6. Link scenes by hand

Asked by Rafael, 2026-10-31: "we need to add sets to scenes, and scenes to
sets". From script… links what the script's text names; the creator can't
yet add or remove a scene of a set, character or prop himself, nor say
what is in the scene he is reading. Only wardrobe has a scene picker (Worn
by, links/3).

- **Type:** code
- **Depends on:** links/1, links/2, links/5 (the links From script makes);
  film-bible/contract/2 (`Bible.link` / `unlink`, `trelby/bible.py:399-416`,
  `Bible.scenes`, `trelby/bible.py:425`); fountain-native/scenes (scene
  numbers); bugs/editor/20, fixed 2026-10-31 (the panel's bible is the
  current tab's film). No new Python package; no `mocap-contracts`
  change (a link is `{scene}`, as From script writes it).
- **Decided (Rafael, 2026-10-31):**
  1. Sets, characters and props (wardrobe keeps Worn by).
  2. The scene side is one checklist of every map.
  3. An unlink is not remembered: From script offers that link again,
     ticked, and the creator unticks it.
- **Contract:**
  - In: the open film's bible and the current tab's script (its numbered
    scenes, `bibleedit.sceneChoices`, `trelby/bibleedit.py:245`).
  - Requires:
    - **Item side:** the form of a set, character or prop shows its
      scenes with a **Scenes…** button (today read-only text,
      `trelby/bibleform.py:124`): a checklist of the script's numbered
      scenes, each as `12 — INT. SPACESHIP - NIGHT` (number and
      heading), plus scenes the item names that the script no longer has,
      ticked where linked; OK links the ticked and unlinks the unticked,
      as `creator`, one change-log entry per item; Cancel writes nothing.
    - **Scene side:** under the panel's scene line (`showScene`,
      `trelby/biblepanel.py:465`), **This scene…**, enabled when the
      cursor is in a numbered scene: one checklist of every set,
      character and prop, grouped by map (child items under their
      parent), ticked where linked to that scene; OK links / unlinks the
      changes only, as `creator`; Cancel writes nothing.
    - After either, the tree, the form and the scene line show the new
      links; a link made by hand is the same record as one From script
      makes.
  - Delivers: no-wx functions in `bibleedit` (the scene choices with
    their headings; `setScenes(b, item, scenes)`, the item linked to
    exactly these scenes; `sceneItems(b, scene)` / `setSceneItems(b,
    scene, ids)` for the scene side, keeping wardrobe's character links
    untouched), the two buttons and dialogs, tests, and the as-built
    (`trelby/CLAUDE.md`, `trelby.process.md` Stage 1).
- **Pre-work:** none: the neutral sample (`trelby/sample.fountain`) and
  the test films made in `tmp_path` are enough.
- **Out of scope:** remembering an unlink (decision 3); a scene heading's
  sub-location (`INT. SPACESHIP - CABIN` reads as `SPACESHIP` for From
  script, the last ` - ` part taken as the time of day,
  `trelby/biblelinks.py:28`; link the scene to a child set by hand); typed scene numbers
  in headings (bugs/import-export/11); wardrobe; the minimap's highlight
  of linked scenes (its own initiative).
- **Tests:** `setScenes` adds and removes exactly the difference and
  leaves other scenes and per-scene values alone; a scene the script no
  longer has stays listed while linked; the scene side links and unlinks
  items of all three maps and never touches a wardrobe item's character
  links; nothing written when nothing changed; the change log has one
  entry per changed item. The dialogs need a display: checked through the
  real window.
