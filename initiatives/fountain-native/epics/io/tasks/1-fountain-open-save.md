## 1. Open and save Fountain natively

- **Type:** code
- **Depends on:** —
- **Contract:**
  - In: a `.fountain` file (spec 1.1, UTF-8)
  - Requires: File → Open/Save read and write Fountain directly (today it is
    import only, and saving writes `.trelby`); every element the editor has
    maps to Fountain (scene, action, character, dialogue, parenthetical,
    transition, shot, note, act break → section `#`), plus title page,
    scene numbers `#n#`, dual dialogue, boneyard and synopses kept as written;
    what the editor cannot show is kept and written back untouched
  - Delivers: Fountain as the default format; a round-trip guarantee
- **Pre-work:** —
- **Out of scope:** scene ids (scenes/1), span notes (notes/1)
- **Tests:** open → save → open is byte-identical on
  `mocap-previz/docs/exploration/script-to-previz/spikes/fountain/sample_ptbr.fountain`
  (copied in as a fixture) and on cases for every element, accents, dual
  dialogue, boneyard, synopses, title page
