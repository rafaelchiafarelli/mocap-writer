## 1. Field catalog

- **Type:** **manual** task (Rafael approves; the session proposes and records).
- **Depends on:** —
- **Contract:**
  - In: Rafael's notes (2026-10-23) and the registers of the mocap-preprod
    agents (character-design-planner, props-continuity-planner,
    visual-development-analyst)
  - Requires: every field has a name, type (text, number+unit, choice, list,
    file, link), whether it repeats per scene, and who fills it; every value
    carries a **state** (`script-stated`, `creator-approved`, `proposal`,
    `TBD`) and a source (scene id or decision), as the mocap-preprod registers
    already do, so AI proposals never pass as approved
  - Delivers: the approved catalog below, edited by Rafael, with the date
- **Pre-work:** —
- **Out of scope:** the file format (contract/2)
- **Tests:** —

### Proposal (to approve, cut or extend)

Every item: `id`, `name`, `aliases`, `description`, `photos/`, `references/`,
`notes`, `tags`, `children` (sub-items), `scenes` (ids, derived from links).

**Set (cenário)**
- Space: interior/exterior, type (house, office, street…), period/era, place
  (country, city, region), time of day it is used at
- Size: width × depth × height (m), floor plan file, `.blend` file, level
  (ground floor, 3rd floor…), ceiling type
- Openings: doors (count, position, which way they open, what they lead to),
  windows (count, size, what is seen outside), stairs
- Surfaces: wall color/finish, floor material, ceiling, wear (new, worn,
  dirty, damaged)
- Style: architecture, decoration style, social class it shows, mood
- Light: natural light sources and direction, practical lights (lamps,
  screens), color temperature
- Sound: room acoustics (echo, carpeted, empty), ambient sound (traffic, rain,
  fridge hum)
- Smell and temperature (for the actors and the writer)
- Furniture and dressing: child items, each with state (`unmade bed`,
  `dirty sofa`, `torn rug`); props from the props map can be placed here too
- Continuity per scene: what changes between scenes (broken window, moved
  sofa)
- Capture: floor area needed, obstacles the actor touches (mocap stand-ins)

**Character (personagem)**
- Identity: name, nicknames, age, gender, pronouns, nationality, social
  class, occupation, role in the story (protagonist, antagonist…)
- Inner life: personality traits, predominant emotions, Jungian archetypes,
  wants vs needs, fears, values, secret, arc (start → end)
- Body: height, build, posture, physicality (heavy, nervous, lazy…), way of
  walking, disability or condition, age marks
- Face (for the animated character): face shape, eye size/shape/color,
  eyebrows, nose size/shape, mouth size, lips, teeth, ears, chin, skin
  color/texture, wrinkles, scars, freckles, facial hair
- Hair: length, color, texture, style, how it moves
- Hands: size, nails, rings, how they gesture
- Voice: pitch, rhythm, accent, catchphrases, verbal tics (feeds mocap-audio)
- Mannerisms and habits; how they react under stress
- Relationships: links to other characters, with the kind of relationship
- Capture: actor who plays it, proportions to retarget (from mocap-blender's
  target skeleton)
- Per scene: emotional state, physical state (wet, hurt, out of breath),
  wardrobe (link)

**Prop (item cênico)** — created from capitalized words in Action
- Identity: category (hand prop, set dressing, vehicle, food…), quantity,
  is it a hero prop (seen in close-up)
- Look: size (cm), shape, color, material (wood, metal, glass, fabric…),
  finish (matte, glossy), drawings/sketches, brand
- Touch: weight, temperature, surface (smooth, rough, sticky, soft), how it
  feels to the character
- Taste and smell (when eaten, drunk or close to the face)
- Sound it makes (feeds mocap-audio)
- Behavior: rigid, flexible, breakable, liquid, cloth (needs simulation)
- Handling: who handles it, how, hand-offs between characters
- State per scene: new, used, broken, full/empty, lit/unlit
- Capture: stand-in object for the actor, `.blend` model

**Wardrobe (figurino)** — linked to a character in a scene
- Pieces: child items (shirt, trousers, shoes, accessories), each with
  garment type, fabric type, color, pattern, fit, brand
- Condition: clean, dirty, torn, wet, ironed
- Meaning: what it says about the character, period, social class
- Behavior: stiff or flowing (cloth simulation), noise it makes
- Files: photos, references, `.blend` model, pattern files
- Changes: which scenes it is worn in, what changes between scenes
- Capture: what the actor wears for capture (markerless: tight vs loose)
