# mocap-writer — initiatives (execution order)

Source: Rafael's review of unmodified Trelby (2026-10-23). Bugs found there
go as fix branches, not initiatives (splash that never closes, tooltips that
start off-screen).

0. **as-built** — documentation of Trelby as forked, in its folders (harpia's model)
1. **pdf-import** — Rafael's existing PDF scripts open in the writer and come out as Fountain
2. **editor-ux** — zoom, dark theme, Tab order, capitalized words in Action
3. **fountain-native** — open/save Fountain as the native format; scene ids and numbering; notes on text spans
4. **film-bible** — the maps (sets, characters, props, wardrobe) as folders in the film root
5. **story-structure** — where we are in the story (acts, beats): a study first

`film-bible` needs `fountain-native/scenes` (scene ids). `pdf-import` and `editor-ux` need nothing.
