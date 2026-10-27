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
    `TBD`) and a source (scene number or decision), as the mocap-preprod registers
    already do, so AI proposals never pass as approved
  - Delivers: the approved catalog below, edited by Rafael, with the date
- **Pre-work:** —
- **Out of scope:** the file format (contract/2)
- **Tests:** —

### Proposal (to approve, cut or extend)

Every item: `id`, `name`, `aliases`, `description`, `photos/`, `references/`,
`notes`, `tags`, `children` (sub-items), `scenes` (numbers, derived from links).

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

### Scene annotations (Rafael, 2026-10-25; proposal to approve, cut or extend)

Inside a scene, an **Action**, a **Transition** or a **Shot** element can
carry annotations. Each annotation is anchored to the element (or to a span
of its text, the notes/1 mechanism), has a **kind**, a short text, links to
bible items, and like every value a **state** and a **source**. Marking in
Fountain (Rafael, 2026-10-26, fountain-native/notes/1): a typed note with
kind, id and a short text, e.g. `[[fx annotation-w-7: chuva forte]]`; the
full fields live in the record in `annotations/` the note points to.

**Action** — annotation kinds:
- **Note** — free text for the writer or the crew
- **Character direction** — character (link), what they do: blocking and
  path (from → to), gesture, look/eyeline, emotion and intensity, timing
  (beat, pause, overlap); feeds mocap capture planning
- **Prop direction** — prop (link), the action on it (picks up, drops,
  breaks, hands over to [character]), state before → after (continuity)
- **Special effect** — practical (rain, smoke, fire, breakaway, squib) or
  visual (digital); description, when it starts and stops, intensity,
  safety notes, who makes it (SFX / VFX)
- **Set direction** — set (link), a change during the scene: dressing
  moved, door opens, light changes (practical on/off, time of day shifts)
- **Sound direction** — a sound effect or ambience cue (feeds mocap-audio)
- **General direction** — anything else for the director

**Transition**
- Types, **one or more combined** (Rafael, 2026-10-25: e.g. a cross-
  dissolve that is also a match cut with an L-cut): cut, match cut (on
  action, shape or sound), jump cut, smash cut, dissolve / cross-dissolve,
  fade in, fade out, fade to black / white, wipe, iris, J-cut / L-cut
  (sound leads or trails); picture and sound can each have their own
- Duration (frames or seconds, at the film's frame rate)
- Sound bridge: what carries over and how (music, dialogue, effect)
- What motivates it (matching element in both shots)
- Description

**Shot** — photographic and machinery description
- Size: extreme close-up, close-up, medium close-up, medium, cowboy, medium
  long, long, extreme long, insert
- Angle: eye level, high, low, overhead / bird's eye, worm's eye, Dutch
  (tilt in degrees); point of view: neutral, POV of [character], over the
  shoulder of [character]
- Subjects in frame (links: characters, props), composition (rule of thirds,
  centered, headroom, lead room), two-shot / group
- Lens: focal length (mm), type (spherical, anamorphic, macro, fisheye),
  aperture (T/f-stop), depth of field, focus (fixed, rack focus from → to,
  split diopter)
- Camera movement: static, pan, tilt, dolly in/out, truck, pedestal, crane /
  jib, zoom, dolly zoom, handheld, steadicam / gimbal, drone, arc around
  [subject]; speed and path
- Support / machinery: tripod, dolly and track, slider, crane, gimbal,
  car mount, drone, motion-control rig
- Frame rate (slow / fast motion), shutter angle, duration, aspect ratio
- Lighting intent: key direction, high-key / low-key, contrast, color
  temperature, practicals in shot
- Previz: the virtual camera for mocap-previz / Blender (sensor, focal
  length, position and path), so a shot description becomes a camera
- Description; references (frames, storyboard images)

Questions for Rafael: should Dialogue and Parenthetical carry character
directions too (they are performance, as much as Action)? Is a Shot always
its own element, or can it also be an annotation on an Action ("the camera
follows her")?

