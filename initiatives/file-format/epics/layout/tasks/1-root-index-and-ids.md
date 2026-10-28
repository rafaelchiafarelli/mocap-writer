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
    record id**: it is named by its permanent scene number (`12.A`,
    fountain-native/scenes/1, Rafael 2026-10-25); no record refers to
    another by path; a file that fails its Harpia message is refused with
    the path of the problem; **opening never breaks** (Rafael,
    2026-10-25): a missing or invalid part or file is collected into a
    list of problems (what, where it was expected, why) and the rest of
    the film opens; only a missing or invalid `film.json` stops the open,
    and then with a message, never a crash
  - Delivers: the library that opens a film root, validates `film.json`,
    tells a program which parts it owns, and hands out new ids
- **Pre-work:** the `mocap-contracts` task above (done, `v0.4.0`) and its
  five open rules (decided 2026-10-28, below: `v0.5.0`). The id form and
  the default part paths are decided (below, Rafael 2026-10-26). The writer
  gets `mocap-contracts` as a git submodule at `third_party/mocap-contracts`
  pinned to its tag, on `PYTHONPATH` in the image, with `protobuf` added to
  `docker/requirements.lock` (Rafael, 2026-10-28: a hashed lock can't hold a
  `git+` URL)
- **Out of scope:** the warning and the search for missing files
  (layout/3); history (layout/2); the contents of each part (their
  own tasks); moving to C (study/3: kept in mind, not built)
- **Tests:** a new film root gets a valid `film.json`; two id spaces never
  collide; a part written by a program that does not own it is refused; an
  invalid file names the broken field; a film with a part and a photo
  deleted opens and lists both problems

### Decided: id form (Rafael, 2026-10-26)

Option A of the session's proposal (2026-10-25), with **one counter per
kind** in each space. Not chosen: B (`<kind>-<n>`, one counter: only the
writer could make ids and a second writer collides), C (3-letter tags,
less readable), D (ULIDs, unreadable).

The id is a **unique identifier, not an index** (Rafael, 2026-10-26):
items are added to and removed from each list and moved from one link to
another, and the id never follows a position. A removed item leaves a gap
that is never filled; moving an item or changing what it is linked to
never changes its id. A scene has no record id: it is named by its scene
number (fountain-native/scenes/1).

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
- **n**, a counter per kind in each space, starting at 1, with no
  padding: the writer's first character is `character-w-1` and its first
  prop is `prop-w-1`. The counters live in `ids/<space>.json` (`next`, one
  entry per kind, e.g. `{"next": {"character": 13, "prop": 4}}`), owned
  by that space's owner. The counter goes up and is saved **before** the
  record is written, so a crash leaves a gap, never a reused number.
- An id never changes: an accepted agent proposal keeps its agent's id, the
  way ISOXML keeps a terminal-made id negative, so the space always says
  who first made the record. A copy gets a new id (film-bible links/4).
- Check on read: `^(set|character|prop|wardrobe|annotation|proposal)-[a-z][a-z0-9]{0,7}-[1-9][0-9]*$`.
  Hyphens only, so an id is also a safe Windows file name.
- **Not chosen:** UUIDs or ULIDs. They are unique with no counter and no
  spaces, but unreadable, and debugging by eye is why ISOXML was picked.
  Both forms move to C (a change log) the same way.

### Decided: default part paths (Rafael, 2026-10-26)

The session's proposal (2026-10-25), confirmed, except that the scene
index and the sync snapshots stay in `bible/` as data of the `bible`
part, not parts of their own (question 3), and `analysis/` stays out of
`film.json` (question 4).

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
| `settings` | `settings/script-settings.json` | writer | fountain-native/settings/1 (was io/2) |
| `bible` | `bible/` | writer | film-bible/contract/2 |
| `annotations` | `annotations/` | writer | film-bible/contract/1 fields, fountain-native/notes/1 anchors (records anchored to the script, nothing in its text, Rafael 2026-10-26) |
| `proposals-<code>` | `proposals/<agent>/` | that agent | open: how agents write proposals |
| `history` | `history/` | writer | layout/2 (reserved, empty until decided) |

The `ids/<space>.json` counters are not parts: each one belongs to its
space's owner by the rule above.

The scene index (`bible/scene-index.json`, preprod-link/contract/1) and
the sync snapshots (`bible/sync/`, preprod-link/sync/1) are files of the
`bible` part, owned by the writer like the rest of it. `analysis/`, where
agents write their brief, worklist and memos in Markdown, is not listed:
layout/1 ignores folders `film.json` doesn't list.

**What it changed:** preprod-link contract/1 no longer lists the index as
a part of its own; sync/1 already writes `bible/sync/`; film-bible
contract/2 keeps `bible/` and the layout/1 id form.

**Questions for Rafael:**
1. ~~The id form `character-w-12`, or UUIDs?~~ Answered 2026-10-26:
   `character-w-12` (above).
2. ~~One counter per space, or one per kind per space?~~ Answered
   2026-10-26: one per kind per space (above).
3. ~~Move the scene index and the sync snapshots out of `bible/` to
   `preprod/`?~~ Answered 2026-10-26: no, they stay in `bible/` as data
   of the `bible` part.
4. ~~The `analysis/` folder: leave it out of `film.json`, or one part per
   agent?~~ Answered 2026-10-26: left out for now.

**Touchpoint:** `mocap-contracts` `session.harpia` already has a
`Character` with a free-form `id` for capture. A bible `character-…` id
could fill it later; nothing in layout/1 depends on that.

### Decided: the five rules the `film` task left open (Rafael, 2026-10-28)

All five, enforced in `mocap-contracts` (`mocap_contracts.rules`, released
as `v0.5.0`), so the writer and every agent run the same checks:
1. Every part whose owner is not `writer` has a space with that owner; a
   space may outlive its part (a code is never reused).
2. `film.json` always holds the `script` part and the `w` space (owner
   `writer`).
3. Part names are a fixed set: `script`, `settings`, `bible`,
   `annotations`, `history`, `proposals-<code>`, where `<code>` is a
   listed space.
4. An owner is `writer` or kebab-case (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`, an
   agent's file name).
5. Paths hold Windows-safe names only: no `<>:"|?*` or control
   characters, no segment ending in a dot or a space, no reserved device
   name (`CON`, `NUL`, `COM1`...).
