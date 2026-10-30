# the film bible (film-bible/contract/2): the maps (sets, characters, props,
# wardrobe) as folders in the film's bible part, one item.json per item, its
# files beside it and its child items in folders inside it. no wx.
#
#   bible/<map folder>/<slug>/item.json         a BibleItem (mocap-contracts)
#   bible/<map folder>/<slug>/photos/...        its files
#   bible/<map folder>/<slug>/<child slug>/...  a child item, same map
#   bible/not-props.json                        NotProps
#
# an item is known by its id, never by its folder: renaming an item renames
# its folder and keeps its id. every value carries its state, source,
# department and who set it; the contract refuses a field the catalog does
# not list. writes go through film.Film, so ownership is checked and the
# change log records them.

import os
import shutil
from pathlib import Path

import mocap_contracts as mc
from mocap_contracts import bible as cb
from mocap_contracts import film as cf

import trelby.relink as relink

MAPS = cb.MAPS

# the folders an item keeps its files in; a child item never takes one of
# these names
FILE_FOLDERS = ("photos", "references", "plans", "blend", "patterns", "drawings")


def state(name):
    return mc.ValueState.Value("VALUE_STATE_" + name.upper().replace("-", "_"))


def stateName(value):
    return mc.ValueState.Name(value).removeprefix("VALUE_STATE_").lower().replace("_", "-")


class Item:
    def __init__(self, msg, folder):
        # the BibleItem message
        self.msg = msg

        # the item's folder, relative to the film root, no trailing "/"
        self.folder = folder

    @property
    def id(self):
        return self.msg.id

    @property
    def name(self):
        return self.msg.name

    @property
    def map(self):
        return cb.map_of(self.msg.id)

    @property
    def parent(self):
        return self.msg.parent if self.msg.HasField("parent") else None

    @property
    def rel(self):
        return self.folder + "/" + cb.ITEM_FILE

    def __repr__(self):
        return "Item(%r, %r)" % (self.id, self.folder)


class Bible:
    def __init__(self, film):
        self.film = film

        # id -> Item
        self.items = {}

        # words marked "not a prop" for the whole film
        self.notProps = []

        self.load()

    # the bible part's folder relative to the film root, no trailing "/"
    def base(self):
        p = self.film.part("bible")

        return p.path.rstrip("/") if p else None

    def mapFolder(self, map_):
        return self.base() + "/" + cb.MAP_FOLDERS[map_]

    # read every item; an invalid or misplaced one is a film problem, never
    # a crash
    def load(self):
        self.items = {}
        self.notProps = []
        base = self.base()

        if base is None or not (self.film.root / base).is_dir():
            return

        for map_ in MAPS:
            folder = self.film.root / self.mapFolder(map_)

            if folder.is_dir():
                self.loadFolder(map_, folder, None)

        rel = base + "/" + cb.NOT_PROPS_FILE

        if (self.film.root / rel).exists():
            try:
                self.notProps = list(
                    mc.from_json(mc.NotProps, self.film.readText(rel)).words
                )
            except mc.ContractError as e:
                self.film.problem(_("Not-a-prop words"), rel, str(e))

        for item in self.items.values():
            self.checkFiles(item)

    def loadFolder(self, map_, folder, parentId):
        for sub in sorted(folder.iterdir()):
            if not sub.is_dir() or (parentId and sub.name in FILE_FOLDERS):
                continue

            path = sub / cb.ITEM_FILE
            rel = path.relative_to(self.film.root).as_posix()

            if not path.exists():
                continue

            try:
                msg = mc.from_json(mc.BibleItem, path.read_text(encoding="utf-8"))
            except mc.ContractError as e:
                self.film.problem(_("Bible item"), rel, str(e))

                continue

            why = None

            if cb.map_of(msg.id) != map_:
                why = _("a %s item in the %s folder") % (cb.map_of(msg.id), map_)
            elif msg.id in self.items:
                why = _("its id %s is also in %s") % (msg.id, self.items[msg.id].rel)
            elif (msg.parent if msg.HasField("parent") else None) != parentId:
                why = _("its parent is %s but its folder is in %s") % (
                    msg.parent or _("none"),
                    parentId or _("the map"),
                )

            if why:
                self.film.problem(_("Bible item"), rel, why)

                continue

            item = Item(msg, sub.relative_to(self.film.root).as_posix())
            self.items[msg.id] = item
            self.loadFolder(map_, sub, msg.id)

    # a file value that points at nothing is a problem the creator can
    # search for (file-format/layout/3)
    def checkFiles(self, item):
        for i, v in enumerate(item.msg.values):
            if self.field(item.map, v.field).type != "file":
                continue

            rel = item.folder + "/" + v.text

            if not (self.film.root / rel).is_file():
                self.film.problem(
                    _("File of %s") % item.name,
                    rel,
                    _("the file is missing"),
                    self.fileRef(item, i, rel),
                )

    def fileRef(self, item, i, rel):
        kind = "image" if isImage(item.msg.values[i].text) else "file"

        def apply(newRel):
            if not newRel.startswith(item.folder + "/"):
                raise ValueError(
                    _("The file must be inside the item's folder %s.") % item.folder
                )

            item.msg.values[i].text = newRel[len(item.folder) + 1 :]
            self.save(item)

        return relink.Ref(_("File of %s") % item.name, rel, kind, apply)

    def field(self, map_, name):
        return cb.fields(map_)[name]

    # the items of map_ with the given parent (None: the top level), by name
    def children(self, map_, parentId=None):
        out = [
            it
            for it in self.items.values()
            if it.map == map_ and it.parent == parentId
        ]

        return sorted(out, key=lambda it: (it.name.lower(), it.id))

    def get(self, rid):
        return self.items.get(rid)

    # a free folder name for name inside folder (rel): not taken by another
    # item, and inside an item not one of its file folders
    def freeSlug(self, folder, name, keep=None):
        base = cb.slug(name)
        slug = base
        n = 2
        inItem = folder not in [self.mapFolder(m) for m in MAPS]

        while True:
            rel = folder + "/" + slug
            taken = (inItem and slug in FILE_FOLDERS) or (
                (self.film.root / rel).exists() and rel != keep
            )

            if not taken:
                return slug

            slug = "%s-%d" % (base, n)
            n += 1

    # a new item of map_ named name, under parent (an Item of the same map)
    # or at the top level; its id comes from the film's counters
    def create(self, map_, name, parent=None, by=None):
        if parent is not None and parent.map != map_:
            raise ValueError(_("A child item must be of its parent's map."))

        msg = mc.BibleItem(id=self.film.newId(map_), name=name)

        if parent is not None:
            msg.parent = parent.id

        folder = parent.folder if parent else self.mapFolder(map_)
        item = Item(msg, folder + "/" + self.freeSlug(folder, name))
        self.save(item, by)
        self.items[item.id] = item

        return item

    # write item.json; the contract refuses an invalid item before anything
    # is written
    def save(self, item, by=None):
        self.film.writeText(item.rel, mc.to_json(item.msg), by)

    # rename an item and its folder; its id does not change
    def rename(self, item, name, by=None):
        old = item.folder
        parentFolder = old.rsplit("/", 1)[0]
        new = parentFolder + "/" + self.freeSlug(parentFolder, name, keep=old)
        item.msg.name = name

        if new != old:
            self.moveFolder(item, new, by)
        else:
            self.save(item, by)

    # move an item (and its children) under newParent (None: the top level)
    def move(self, item, newParent, by=None):
        if newParent is not None:
            if newParent.map != item.map:
                raise ValueError(_("A child item must be of its parent's map."))

            if newParent is item or newParent.folder.startswith(item.folder + "/"):
                raise ValueError(_("An item can't be moved into itself."))

            item.msg.parent = newParent.id
            folder = newParent.folder
        else:
            item.msg.ClearField("parent")
            folder = self.mapFolder(item.map)

        self.moveFolder(item, folder + "/" + self.freeSlug(folder, item.name), by)

    # move item's folder to new (rel) and rewrite its item.json there; the
    # log shows the old item.json deleted and the new one created
    def moveFolder(self, item, new, by):
        old = item.folder
        mc.to_json(item.msg)
        self.film.checkWrite(old + "/" + cb.ITEM_FILE)
        self.film.checkWrite(new + "/" + cb.ITEM_FILE)
        self.film.deleteFile(old + "/" + cb.ITEM_FILE, by)
        (self.film.root / new).parent.mkdir(parents=True, exist_ok=True)
        os.rename(self.film.root / old, self.film.root / new)

        for it in self.items.values():
            if it.folder == old or it.folder.startswith(old + "/"):
                it.folder = new + it.folder[len(old) :]

        self.save(item, by)

    # delete an item with its files and its children
    def delete(self, item, by=None):
        for child in self.children(item.map, item.id):
            self.delete(child, by)

        self.film.deleteFile(item.rel, by)
        shutil.rmtree(self.film.root / item.folder)
        del self.items[item.id]

    # copy the file at src into the item's sub folder; returns its path
    # relative to the item's folder, for a file value
    def addFile(self, item, src, sub="photos"):
        src = Path(src)
        folder = item.folder + "/" + sub
        name = src.name
        stem, ext = os.path.splitext(name)
        n = 2

        while (self.film.root / folder / name).exists():
            name = "%s-%d%s" % (stem, n, ext)
            n += 1

        rel = folder + "/" + name
        self.film.checkWrite(rel)
        cf.check_path(rel)
        (self.film.root / folder).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, self.film.root / rel)

        return sub + "/" + name

    # the values of field (in scene, for a per-scene field)
    def values(self, item, field, scene=None):
        return [
            v
            for v in item.msg.values
            if v.field == field and (v.scene if v.HasField("scene") else None) == scene
        ]

    # set field's value(s) in scene: values is a list of text (or of
    # (number, unit) for a number field); an empty list clears the field.
    # state, source and by are the same for each; the department is the
    # catalog's for the field unless given.
    def setValues(
        self, item, field, values, state_, source, by, scene=None, department=None,
        revisit=None, note=None, save=True,
    ):
        f = self.field(item.map, field)
        keep = [
            v
            for v in item.msg.values
            if not (v.field == field and (v.scene if v.HasField("scene") else None) == scene)
        ]
        new = []

        for value in values:
            v = mc.BibleValue(
                field=field,
                state=state(state_),
                source=source,
                department=department or f.department,
                by=by,
            )

            if scene is not None:
                v.scene = scene

            if f.type == "number":
                v.number, v.unit = value
            else:
                v.text = value

            if revisit:
                v.revisit = revisit

            if note:
                v.note = note

            new.append(v)

        old = list(item.msg.values)
        del item.msg.values[:]
        item.msg.values.extend(keep + new)

        try:
            mc.to_json(item.msg)
        except mc.ContractError:
            del item.msg.values[:]
            item.msg.values.extend(old)

            raise

        if save:
            self.save(item, by)

    # approve a proposal: its state only changes, to creator-approved
    def approve(self, item, value, by="creator"):
        value.state = state("creator-approved")
        self.save(item, by)

    # link the item to a scene (for wardrobe, with the character who wears
    # it there); no-op if it is linked already
    def link(self, item, scene, character=None, by=None):
        for l in item.msg.links:
            if l.scene == scene and (l.item if l.HasField("item") else None) == character:
                return

        link = item.msg.links.add(scene=scene)

        if character is not None:
            link.item = character

        try:
            self.save(item, by)
        except mc.ContractError:
            del item.msg.links[-1]

            raise

    def unlink(self, item, scene, character=None, by=None):
        for i, l in enumerate(item.msg.links):
            if l.scene == scene and (l.item if l.HasField("item") else None) == character:
                del item.msg.links[i]
                self.save(item, by)

                return

    # the scene numbers the item is in: its links and its per-scene values
    def scenes(self, item):
        nums = {l.scene for l in item.msg.links}
        nums |= {v.scene for v in item.msg.values if v.HasField("scene")}

        return nums

    # rename scenes in every record that names them (fountain-native/
    # scenes/5): moves is {old number: new number}, applied all at once so
    # 1 -> 2 and 2 -> 3 never meet. returns the items changed.
    def renameScenes(self, moves, by="writer"):
        changed = []

        for it in self.items.values():
            touched = False

            for l in it.msg.links:
                if l.scene in moves:
                    l.scene = moves[l.scene]
                    touched = True

            for v in it.msg.values:
                if v.HasField("scene") and v.scene in moves:
                    v.scene = moves[v.scene]
                    touched = True

            if touched:
                changed.append(it)

        for it in changed:
            self.save(it, by)

        return changed

    def saveNotProps(self, by=None):
        rel = self.base() + "/" + cb.NOT_PROPS_FILE
        self.film.writeText(rel, mc.to_json(mc.NotProps(words=self.notProps)), by)


def isImage(text):
    return Path(text).suffix.lower() in relink.KINDS["image"]
