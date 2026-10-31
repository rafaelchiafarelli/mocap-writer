# film-bible — mocap-writer

**Status:** In progress — implemented 2026-10-28 (contract, tree, maps,
links 1–5); links/6, linking scenes by hand, planned 2026-10-31 and
ready to implement; then the initiative gate, Rafael's (below). The maps are
folders in the film's `bible/` part, read and written through
`mocap-contracts` `v0.5.0` (`bible.harpia`, `catalog/bible-v1.json`).

**Goal:** the writer keeps the film's maps (sets, characters, props,
wardrobe) next to the script, as a tree like Windows Explorer: every item is a
folder that holds its data, photos, floor plans, `.blend` files and child
items. Items are linked to scenes, and they can be copied inside a film or to
another film, linked or not.

**Decided (Rafael, 2026-10-23):** the maps are **folders in the film root**
(`<film-root>/bible/`), with their format defined as a Harpia contract. The
Fountain script never holds map data; the maps point to scene **numbers** (permanent, the scene's identity).

**Scope:** the field catalog, the contract, the tree panel, one editor per map,
links (scene ↔ set, prop words → props, wardrobe ↔ character × scene, and
by hand from an item or a scene), copy with warnings.

**Out of scope:** AI filling the maps (mocap-preprod agents propose, the
creator approves: their output lands in these same records with state
`proposal`); 3D asset making; the scene map's own view of shots (mocap-previz).

**Initiative gate:** on the neutral sample, Rafael creates one item of each
map, links it to scenes (From script and by hand), copies one to a second film root, and the
mocap-preprod agents can read the records.

Epics: `epics/README.md`.
