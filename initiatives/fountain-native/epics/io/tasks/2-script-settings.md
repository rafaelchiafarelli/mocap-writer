## 2. Per-script settings with a Fountain script

- **Status:** Planned — re-planned after the file-format decision
  (option A, 2026-10-25): the settings are a record in the film root.

- **Type:** code
- **Depends on:** io/1; file-format/layout/1 (root index, part
  ownership); a `mocap-contracts` task for a `script_settings` message,
  done and tagged
- **Decision (Rafael, 2026-10-25):** first a sidecar file next to the
  script; **replaced** the same day by the file-format decision (option A):
  the settings are a Harpia message, a part of the film root listed in
  `film.json` and owned by the writer.
- **Problem:** a `.trelby` file carries per-script settings: page setup and
  element styles (`Config`), auto-completion lists, locations, the script's
  spell-checker words, page headers. Fountain has no place for them, so
  after io/1 a `.fountain` opens with defaults and none of them is saved.
- **Contract:**
  - In: a `.fountain` script and its settings record in the film root
  - Requires: open restores them, save writes them as a `script_settings`
    message in the part `film.json` lists for them; the Fountain text
    itself is still byte-identical after open → save; a script opened
    outside a film root opens with defaults, as today
  - Delivers: settings that survive the round trip
- **Pre-work:** the `mocap-contracts` task above; the record's fields
  (the `Config` and lists named in Problem), proposed below, to confirm
- **Tests:** settings changed → saved → reopened equal; the script text
  unchanged

### Proposal: the record's fields (session, 2026-10-25; Rafael to confirm)

Read from the code as it is: `Config` (`trelby/config.py:432`), `Type`
and `TextType` (`trelby/config.py:179`, `:157`), `PDFFontInfo`
(`trelby/config.py:367`), `Headers` (`trelby/headers.py:6`),
`AutoCompletion` (`trelby/autocompletion.py:8`), `Locations`
(`trelby/locations.py:10`) and the script's `scDict`
(`trelby/screenplay.py:57`). Names follow `mocap-contracts`: snake_case,
units in the field name, `Flag` for on/off (Harpia has no boolean), every
enum starting at `UNSET`. Defaults are today's `Config` defaults.

**`ScriptSettings`** (a `script_settings` message), at
`settings/script-settings.json` (layout/1's default part path):

- `page`: `paper_width_mm` (210), `paper_height_mm` (297),
  `margin_top_mm` (12.7), `margin_bottom_mm` (25.4), `margin_left_mm`
  (38.1), `margin_right_mm` (25.4), `font_size_pt` (12),
  `page_break_action_lines` (2), `page_break_dialogue_lines` (2),
  `scene_continueds` (off), `scene_continued_indent_chars` (45).
- `elements`, one `ElementStyle` per element (`ELEMENT_SCENE`, `ACTION`,
  `CHARACTER`, `DIALOGUE`, `PAREN`, `TRANSITION`, `SHOT`, `ACT_BREAK`,
  `NOTE`): `before_spacing_tenths` (empty space before, in tenths of a
  line), `intra_spacing_tenths`, `indent_chars`, `width_chars`, and two
  `TextStyle`s, `screen` and `export`, each with `caps`, `bold`,
  `italic`, `underlined`. The `newTypeEnter`/`newTypeTab` keys are global
  (`TypeGlobal`), not per script, so they stay out.
- `pdf`: `show_scene_numbers`, `include_toc`, `show_toc`,
  `open_on_current_page`, `remove_notes`, `outline_notes`,
  `show_margins`, `show_line_numbers`; `fonts`, four `PdfFont`
  (`normal`, `bold`, `italic`, `bold_italic`), each `pdf_name` and
  `filename` (the font to embed; empty uses Courier).
- `strings`: `more` (`(MORE)`), `continued_page_end` (`(CONTINUED)`),
  `continued_page_start` (`CONTINUED:`), `dialogue_continued`
  (` (cont'd)`).
- `headers`: `empty_lines_after` (1), and `HeaderString`s, each `line`
  (1–5), `x_offset_chars`, `align` (`ALIGN_LEFT`/`CENTER`/`RIGHT`),
  `bold`, `italic`, `underlined`, `text` (`${PAGE}` is the page number).
  The default is one header, `${PAGE}.` on line 1, right-aligned.
- `auto_completion`, one list per element that has one (`SCENE`,
  `CHARACTER`, `TRANSITION`, `SHOT`): `enabled`, `items` (the
  transitions default to today's thirteen).
- `locations`: a list of `Location`s, each a list of scene headings
  joined into one location (`INT. ROOM 413 - DAY` with `… - NIGHT`).
- `spelling_words`: the script's own spell-checker words.

**Rules:**
- **Every field is written**, defaults included. The file then says the
  whole layout by itself, and a default changed in code later never moves
  an existing film's page breaks.
- Strings are **Unicode**. Today `strMore`, the `String/…` values, the
  completion items, locations and words are Latin-1 (`StrLatin1Var`);
  that limit goes away for the record (Portuguese accents). `pdf_name`
  stays restricted to the characters a PDF font name allows
  (`PDFFontInfo.refresh`, `trelby/config.py:423`).
- **Out of range is refused, not clamped.** Trelby clamps silently
  (`Config.recalc`). Here a value outside today's limits (e.g.
  `font_size_pt` 4–72, `indent_chars` 0–80) fails validation with its
  field's path; the script then opens with defaults and the problem is
  listed (layout/1's "opening never breaks").

**Left out (questions 1–3 below):** `cursorLine`/`cursorColumn` and the
title page's layout.

**Questions for Rafael:**
1. The cursor position (`Config.cursorLine`/`cursorColumn`, saved by
   nothing today, a known quirk): leave it out (recommended; it is one
   person's view, not the script's, and belongs in per-user state, not a
   film record that a team will share), or put it in the record?
2. The title page's layout (each string's x, y, size, font, alignment,
   `trelby/titles.py`): Fountain keeps only the `Key: value` text, and a
   title page edited in the Titles dialog is written back as text in
   Trelby's default layout (`generateTitle`, `trelby/fountain.py:390`).
   Leave the layout out (recommended; the Fountain title page stays the
   source of truth), or keep it in the record so a custom title layout
   survives?
3. Locations name scenes by their heading text, as Trelby does. With
   permanent scene numbers (scenes/1) they could name scene numbers
   instead, but then a location means "these scenes", not "this place",
   which overlaps the bible's sets (film-bible links/1). Keep headings
   (recommended, as today), or drop locations once sets exist?
4. Approve, cut or extend the list above.
