## 1. Root index and id scheme

- **Type:** code, here and in `mocap-contracts`
- **Depends on:** study/3 (decision A); a `mocap-contracts` task for
  `film.harpia` (the root index and the id rules), done and tagged
- **Contract:**
  - In: a film root
  - Requires: `<film-root>/film.json`, a `film` message, as ISOXML's
    `TASKDATA.XML`: format version, origin (program and version that last
    wrote it), and the parts of the film (script, bible, settings, preprod,
    history...), each with its path and its **owner** (the writer, or a
    named agent), so no two programs write the same part; record ids are
    **typed and stable** (a prefix per kind: set, character, prop,
    wardrobe, annotation...) with a **separate id space per writer
    or agent**, so records made apart never collide (ISOXML's negative ids
    for terminal-made records); ids are never reused; a **scene has no
    record id**: it is named by its permanent scene number (`12A`,
    fountain-native/scenes/1, Rafael 2026-10-25); no record refers to
    another by path; a file that fails its Harpia message is refused with
    the path of the problem; **opening never breaks** (Rafael,
    2026-10-25): a missing or invalid part or file is collected into a
    list of problems (what, where it was expected, why) and the rest of
    the film opens; only a missing or invalid `film.json` stops the open,
    and then with a message, never a crash
  - Delivers: the library that opens a film root, validates `film.json`,
    tells a program which parts it owns, and hands out new ids
- **Pre-work:** Rafael confirms the id form and the default part paths
  (proposed below, to confirm); the `mocap-contracts` task above
- **Out of scope:** the warning and the search for missing files
  (layout/3); history (layout/2); the contents of each part (their
  own tasks); moving to C (study/3: kept in mind, not built)
- **Tests:** a new film root gets a valid `film.json`; two id spaces never
  collide; a part written by a program that does not own it is refused; an
  invalid file names the broken field; a film with a part and a photo
  deleted opens and lists both problems

### Proposal: id form and default part paths (session, 2026-10-25; Rafael to confirm)

**Id form:** `<kind>-<space>-<n>`, e.g. `character-w-12`, `prop-pcp-3`.
- **kind**, a readable word, not a 3-letter tag (study/1, ISOXML answer):
  `set`, `character`, `prop`, `wardrobe`, `annotation`, `proposal`. A new
  kind is a change to `film.harpia`, never made up by a program.
- **space**, who made the record: `w` for the writer; each agent gets a
  short code (1–8 lower-case letters or digits, starting with a letter)
  when its part is added to the film, e.g. `pcp` for
  `props-continuity-planner`. `film.json` maps every code to its owner.
  A code is never reused, even after its agent leaves the film. A second
  writer later (team work) gets its own code (`w2`), so no records made
  apart ever collide.
- **n**, a counter per space, shared by all kinds, starting at 1, with no
  padding. It lives in `ids/<space>.json` (`next`), owned by that space's
  owner. The counter goes up and is saved **before** the record is
  written, so a crash leaves a gap, never a reused number.
- An id never changes: an accepted agent proposal keeps its agent's id, the
  way ISOXML keeps a terminal-made id negative, so the space always says
  who first made the record. A copy gets a new id (film-bible links/4).
- Check on read: `^(set|character|prop|wardrobe|annotation|proposal)-[a-z][a-z0-9]{0,7}-[1-9][0-9]*$`.
  Hyphens only, so an id is also a safe Windows file name.
- **Not chosen:** UUIDs or ULIDs. They are unique with no counter and no
  spaces, but unreadable, and debugging by eye is why ISOXML was picked.
  Both forms move to C (a change log) the same way.

**`film.json`** (a `film` message):
- `format_version` (int, `1`); `origin`: `program` and `version` of the
  last program that wrote it;
- `parts`: `name`, `path`, `owner` (`writer` or an agent name as in
  `mocap-preprod/.claude/agents/`);
- `spaces`: `code`, `owner`.
- The writer owns `film.json`: adding a part or a space is a writer
  action. Agents read `film.json` and never write it.

**Paths:** relative to the film root, `/` as separator, never leaving the
root (no `..`, no drive letter), so a film copied from `G:` to WSL or to
another person still opens. **A part's path is never inside another
part's path**, so each file has one owner and ownership is a prefix check.

**Default parts** for a new film (a film can point a part somewhere else,
e.g. an existing script's own name):

| Part | Path | Owner | Planned in |
|---|---|---|---|
| `script` | `script.fountain` | writer | fountain-native/io/1 |
| `settings` | `settings/script-settings.json` | writer | fountain-native/io/2 |
| `bible` | `bible/` | writer | film-bible/contract/2 |
| `annotations` | `annotations/` | writer | film-bible/contract/1 (if study/1 option A, records pointed to by notes, is confirmed) |
| `scene-index` | `preprod/scene-index.json` | writer | preprod-link/contract/1 (today `bible/scene-index.json`) |
| `sync` | `preprod/sync/` | writer | preprod-link/sync/1 (today `bible/sync/`) |
| `proposals-<code>` | `proposals/<agent>/` | that agent | open: how agents write proposals |
| `history` | `history/` | writer | layout/2 (reserved, empty until decided) |

The `ids/<space>.json` counters are not parts: each one belongs to its
space's owner by the rule above.

**What it changes if confirmed:** preprod-link contract/1 and sync/1 move
from `bible/` to `preprod/` (a part may not sit inside `bible/`);
film-bible contract/2 keeps `bible/` and gains the id form. Their task
files are edited when this is confirmed, not before.

**Questions for Rafael:**
1. The id form `character-w-12` (recommended), or UUIDs?
2. One counter per space (recommended: simpler, one file per owner), or
   one per kind per space (`character-w-1`, `prop-w-1`)?
3. Move the scene index and the sync snapshots out of `bible/` to
   `preprod/`?
4. The `analysis/` folder that agents already write (brief, worklist,
   memos in Markdown): leave it out of `film.json` for now (recommended:
   they are not Harpia records, and layout/1 ignores folders it doesn't
   list), or list it as one part per agent?

**Touchpoint:** `mocap-contracts` `session.harpia` already has a
`Character` with a free-form `id` for capture. A bible `character-…` id
could fill it later; nothing in layout/1 depends on that.
