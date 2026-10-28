## 5. Find characters

- **Status:** Done (2026-10-28) — `biblelinks.characterPlan`, From script →
  Find characters

- **Type:** code
- **Asked by:** Rafael, 2026-10-28, before testing the bible on an
  imported script: no command made characters from the script
- **Depends on:** links/1–3 (the plan-then-checklist pattern, `biblelinks`)
- **Contract:**
  - In: the Character elements of the numbered scenes
  - Requires: the speaking name without its extension (`ANA (V.O.)`,
    `ANA (CONT'D)`) and without the dual-dialogue `^` is the character;
    a name the bible knows (name or alias, case and accents ignored)
    links the character to the scenes it speaks in; an unknown name is
    offered as a new character with its scenes (state of the links: the
    script), unticked, never made silently; the new character is named as
    the script writes it, like sets and props
  - Delivers: `biblelinks.characterPlan` / `createCharacters`, From script
    → Find characters
- **Pre-work:** —
- **Out of scope:** characters named in Action but never speaking; the
  character's fields
- **Tests:** extensions and `^` stripped; known name linked; unknown
  offered and not made; made characters linked to their scenes; aliases
