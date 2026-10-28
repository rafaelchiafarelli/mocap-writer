# what the bible form edits (film-bible/maps), without wx: the catalog's
# groups and fields of a map, each field's values as text and back, and the
# creator's edits as values with their state, source and author. the form
# (bibleform.py) is generated from this, so a catalog change needs no new
# form code.

import datetime
import re

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
