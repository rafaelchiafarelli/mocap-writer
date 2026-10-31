# what the bible form edits (film-bible/maps), without wx: the catalog's
# groups and fields of a map, each field's values as text and back, and the
# creator's edits as values with their state, source and author. the form
# (bibleform.py) is generated from this, so a catalog change needs no new
# form code.

import datetime
import re

import mocap_contracts as mc

import trelby.bible as bible
import trelby.scenenumbers as scenenumbers

# list values are shown and typed separated by this
LIST_SEP = "; "

# the states a value can have, in the order the form offers them
STATES = ("script-stated", "creator-approved", "proposal", "tbd")

# the sub folder of an item a file field's files are copied into
FILE_FOLDERS = {
    "general.photos": "photos",
    "general.references": "references",
    "size.floor_plan": "plans",
    "look.drawings": "drawings",
    "files.patterns": "patterns",
}

# the maps whose items are linked to scenes by hand (links/6); wardrobe
# keeps Worn by
SCENE_MAPS = ("set", "character", "prop")

DECIMAL = re.compile(r"^-?[0-9]+([.,][0-9]+)?$")


class Group:
    def __init__(self, key, label, perScene, fields):
        self.key = key
        self.label = label
        self.perScene = perScene

        # [bible's catalog Field]
        self.fields = fields


# the groups of map_, in catalog order
def groups(map_):
    out = []

    for f in bible.cb.fields(map_).values():
        if not out or out[-1].key != f.group:
            out.append(Group(f.group, f.group_label, f.per_scene, []))

        out[-1].fields.append(f)

    return out


def field(map_, name):
    return bible.cb.fields(map_)[name]


# the values of name in scene as text: a list joined by LIST_SEP, a number
# without its unit (the form shows the unit), a link as the item's name, a
# file as its path in the item's folder
def text(b, item, name, scene=None):
    f = field(item.map, name)
    out = []

    for v in b.values(item, name, scene):
        if f.type == "number":
            out.append(v.number)
        elif f.type == "link":
            it = b.get(v.text)
            out.append(it.name if it else v.text)
        else:
            out.append(v.text)

    return LIST_SEP.join(out)


# the values a text typed in the form stands for: [str], or [(number,
# unit)] for a number field. a list field splits on ";". raises ValueError
# for a number that is not one.
def parse(f, s):
    s = s.strip()

    if not s:
        return []

    if f.type == "list":
        return [p.strip() for p in s.split(";") if p.strip()]

    if f.type == "number":
        if not DECIMAL.match(s):
            raise ValueError(_("%s is not a number: %s") % (f.label, s))

        return [(s.replace(",", "."), f.unit)]

    return [s]


# what the creator's edits are stamped with
def creatorSource(today=None):
    today = today or datetime.date.today()

    return _("creator %s") % today.isoformat()


# the creator typed s for name in scene: store it if it differs, as
# creator-approved. returns True if anything changed.
def commit(b, item, name, s, scene=None, today=None):
    f = field(item.map, name)
    new = parse(f, s)
    old = [(v.number, v.unit) if f.type == "number" else v.text for v in b.values(item, name, scene)]

    if new == old:
        return False

    b.setValues(
        item, name, new, "creator-approved", creatorSource(today), "creator", scene=scene
    )

    return True


# the state of name's values in scene (the first value's), or None if it
# has none
def stateOf(b, item, name, scene=None):
    vs = b.values(item, name, scene)

    return bible.stateName(vs[0].state) if vs else None


# the tooltip of a field: its state, source, author and department, or that
# it is empty
def describe(b, item, name, scene=None):
    vs = b.values(item, name, scene)

    if not vs:
        return _("No value yet.")

    v = vs[0]
    lines = [
        _("State: %s") % bible.stateName(v.state),
        _("Source: %s") % v.source,
        _("Set by: %s") % v.by,
        _("Department: %s") % v.department,
    ]

    if v.HasField("revisit"):
        lines.append(_("Revisit when: %s") % v.revisit)

    for v in vs:
        if v.HasField("note"):
            lines.append("%s: %s" % (v.text, v.note))

    return "\n".join(lines)


# set the state of name's values in scene; a script-stated value gets its
# source (the scene number that states it), a TBD one its revisit trigger.
# only the state, source and revisit change.
def setState(b, item, name, stateName_, scene=None, source=None, revisit=None):
    vs = b.values(item, name, scene)

    if not vs:
        return

    old = [type(v)() for v in vs]

    for o, v in zip(old, vs):
        o.CopyFrom(v)

    for v in vs:
        v.state = bible.state(stateName_)

        if source:
            v.source = source

        if revisit:
            v.revisit = revisit
        elif stateName_ != "tbd":
            v.ClearField("revisit")

    try:
        b.save(item, "creator")
    except Exception:
        for o, v in zip(old, vs):
            v.CopyFrom(o)

        raise


# [(id, name)] of the items name can link to, by name; never the item itself
def linkChoices(b, item, name):
    f = field(item.map, name)
    out = [
        (it.id, it.name)
        for it in b.items.values()
        if it.map == f.link_kind and it.id != item.id
    ]

    return sorted(out, key=lambda x: (x[1].lower(), x[0]))


# link name to the items ids (in scene); the links kept keep their notes
def setLinks(b, item, name, ids, scene=None):
    keep = {v.text: v.note for v in b.values(item, name, scene) if v.HasField("note")}

    if [v.text for v in b.values(item, name, scene)] == list(ids):
        return False

    b.setValues(
        item, name, list(ids), "creator-approved", creatorSource(), "creator",
        scene=scene, save=False,
    )

    for v in b.values(item, name, scene):
        if v.text in keep:
            v.note = keep[v.text]

    b.save(item, "creator")

    return True


# copy files into the item and add them to the file field name
def addFiles(b, item, name, paths, scene=None):
    sub = FILE_FOLDERS.get(name) or ("blend" if name.endswith(".blend") else "files")
    rels = [v.text for v in b.values(item, name, scene)]

    for p in paths:
        rels.append(b.addFile(item, p, sub))

    b.setValues(item, name, rels, "creator-approved", creatorSource(), "creator", scene=scene)


def removeFile(b, item, name, rel, scene=None):
    rels = [v.text for v in b.values(item, name, scene) if v.text != rel]
    b.setValues(item, name, rels, "creator-approved", creatorSource(), "creator", scene=scene)
    path = b.film.root / item.folder / rel

    if path.is_file():
        path.unlink()


# the scene numbers a per-scene group can be filled for: the item's scenes
# and the open script's, in script order
def sceneChoices(b, item, sp=None):
    nums = set(b.scenes(item))

    if sp is not None:
        nums |= {n for _l, n in scenenumbers.scenesOf(sp) if n}

    return sorted(nums, key=lambda n: scenenumbers.key(n) or (999999, n))


# the scenes a wardrobe item is worn in by the character cid
def wornScenes(item, cid):
    return [l.scene for l in item.msg.links if l.HasField("item") and l.item == cid]


# "Ana in 1, 2; Bia in 3": who wears a wardrobe item where
def wornText(b, item):
    byChar = {}

    for l in item.msg.links:
        if l.HasField("item"):
            byChar.setdefault(l.item, []).append(l.scene)

    parts = []

    for cid, scenes in byChar.items():
        c = b.get(cid)
        parts.append(_("%s in %s") % (c.name if c else cid, ", ".join(scenes)))

    return LIST_SEP.join(sorted(parts))


# the wardrobe item is worn by character in exactly scenes
def setWorn(b, item, character, scenes):
    old = set(wornScenes(item, character.id))

    for s in sorted(old - set(scenes)):
        b.unlink(item, s, character.id, "creator")

    for s in scenes:
        if s not in old:
            b.link(item, s, character.id, "creator")


# links/6: scenes by hand

# {scene number: heading text} of the open script's numbered scenes, in
# script order
def sceneHeadings(sp):
    out = {}

    for line, num in scenenumbers.scenesOf(sp):
        if num:
            last = sp.getElemLastIndexFromLine(line)
            out[num] = " ".join(sp.lines[i].text for i in range(line, last + 1))

    return out


# the item's scene choices as [(number, "12 — INT. ROOM - DAY")]: the
# script's numbered scenes and the scenes the item names that the script no
# longer has (the number alone)
def sceneLabels(b, item, sp=None):
    heads = sceneHeadings(sp) if sp is not None else {}

    return [
        (n, "%s \u2014 %s" % (n, heads[n]) if n in heads else n)
        for n in sceneChoices(b, item, sp)
    ]


# the scenes the item is linked to (not its per-scene values, not
# wardrobe's links with a character)
def linkedScenes(item):
    return [l.scene for l in item.msg.links if not l.HasField("item")]


# link item to exactly scenes, in one write (one change-log entry); returns
# True if anything changed. the item is put back if the contract refuses it
def setScenes(b, item, scenes, by="creator"):
    want = set(scenes)
    old = set(linkedScenes(item))

    if want == old:
        return False

    before = item.msg.SerializeToString()
    keep = [l for l in item.msg.links if l.HasField("item") or l.scene in want]
    del item.msg.links[:]
    item.msg.links.extend(keep)

    for s in sorted(want - old, key=lambda n: scenenumbers.key(n) or (999999, n)):
        item.msg.links.add(scene=s)

    try:
        b.save(item, by)
    except mc.ContractError:
        item.msg.ParseFromString(before)

        raise

    return True


# the ids of the sets, characters and props linked to scene
def sceneItems(b, scene):
    return {
        it.id
        for it in b.items.values()
        if it.map in SCENE_MAPS and scene in linkedScenes(it)
    }


# the scene side's choices: [(item, depth)] per map in SCENE_MAPS, child
# items under their parent, by name
def sceneItemChoices(b):
    out = []

    def walk(map_, parentId, depth):
        for it in b.children(map_, parentId):
            out.append((it, depth))
            walk(map_, it.id, depth + 1)

    for map_ in SCENE_MAPS:
        walk(map_, None, 0)

    return out


# the sets, characters and props linked to scene are exactly ids; only the
# items whose link changes are written. returns the items changed
def setSceneItems(b, scene, ids, by="creator"):
    ids = set(ids)
    changed = []

    for it in list(b.items.values()):
        if it.map not in SCENE_MAPS:
            continue

        scenes = set(linkedScenes(it))
        want = scenes | {scene} if it.id in ids else scenes - {scene}

        if want != scenes and setScenes(b, it, want, by):
            changed.append(it)

    return changed
