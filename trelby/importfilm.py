# an import that ends in a complete film (import-to-film), no wx: the
# original file copied into the film, and one plan of everything the
# script offers to the bible (sets, characters, props: links to known items
# and new items with their scenes), applied in one go with the creator's
# choices, and the report of what was made and what still needs the
# creator.

import os
import shutil

import trelby.biblelinks as biblelinks
import trelby.scenenumbers as scenenumbers
import trelby.screenplay as screenplay

SOURCE_PART = "source"
SOURCE_PATH = "source/"


# copy the imported file into the film's source part (added when the film
# has none); returns its path relative to the film root
def copySource(f, path):
    if f.part(SOURCE_PART) is None:
        f.addPart(SOURCE_PART, SOURCE_PATH)

    rel = f.part(SOURCE_PART).path.rstrip("/") + "/" + os.path.basename(path)
    f.checkWrite(rel)
    (f.root / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, f.root / rel)

    return rel


class Section:
    def __init__(self, map_, links, new):
        self.map = map_

        # [(item, scene)] links to known items
        self.links = links

        # {name: [scenes]} new items, named as the script writes them
        self.new = new

    # the lines of the review: ("link", (item, scene)) or ("new", (name,
    # scenes)), links first
    def lines(self):
        return [("link", l) for l in self.links] + [("new", n) for n in self.new.items()]


# the review's plan (task 2): sets, characters, props, each made before
# anything is applied, so a character made here is never offered as a prop
def plan(b, sp):
    sl, sn = biblelinks.setPlan(b, sp)
    cl, cn = biblelinks.characterPlan(b, sp)
    pl, pn = biblelinks.propPlan(b, sp)
    newChars = {biblelinks.norm(n) for n in cn}
    pn = {run: nums for run, nums in pn.items() if biblelinks.norm(run) not in newChars}

    return [Section("set", sl, sn), Section("character", cl, cn), Section("prop", pl, pn)]


# apply the chosen lines of each section ({map: [line index]}); with
# linkScenes False (an import into an open film, whose scene numbers are
# not this script's) new items are made without scenes and no link is
# made. the new props left unticked are marked "not a prop" when
# notProps. returns {map: [items made]}
def apply(b, sections, chosen, notProps=False, linkScenes=True, by="creator"):
    made = {}

    for sec in sections:
        lines = sec.lines()
        pick = set(chosen.get(sec.map, ()))
        links = [l for i, (k, l) in enumerate(lines) if k == "link" and i in pick]
        new = dict(n for i, (k, n) in enumerate(lines) if k == "new" and i in pick)

        if linkScenes:
            biblelinks.applyLinks(b, links, by)
        else:
            new = {name: [] for name in new}

        make = {"set": biblelinks.createSets, "character": biblelinks.createCharacters,
                "prop": biblelinks.createProps}[sec.map]
        made[sec.map] = make(b, new, by)

        if sec.map == "prop" and notProps:
            left = [n for i, (k, (n, _s)) in enumerate(lines) if k == "new" and i not in pick]

            if left:
                biblelinks.markNotProps(b, left, by)

    return made


# the lines of the script holding an IMPORT: note (the PDF importer's
# doubtful spots)
def importNotes(sp):
    return [
        i for i, l in enumerate(sp.lines)
        if l.lt == screenplay.NOTE and sp.isFirstLineOfElem(i) and l.text.startswith("IMPORT:")
    ]


# the report (task 3) as text
def report(b, sp, made):
    scenes = biblelinks.scenesWithLines(sp)
    unnumbered = sum(1 for _l, n in scenenumbers.scenesOf(sp) if not n)
    notes = importNotes(sp)
    out = [_("Scenes: %d, numbered %s.") % (
        len(scenes), "%s-%s" % (scenes[0][0], scenes[-1][0]) if scenes else "-")]

    if unnumbered:
        out.append(_("Scenes with no number yet: %d (save the script).") % unnumbered)

    out.append(_("IMPORT: notes to check: %d.") % len(notes))
    out.append("")
    labels = {"set": _("Sets made"), "character": _("Characters made"), "prop": _("Props made")}

    for map_ in ("set", "character", "prop"):
        items = made.get(map_, [])
        out.append("%s: %d%s" % (labels[map_], len(items),
                                 (" (" + ", ".join(it.name for it in items) + ")") if items else ""))

    out.append("")
    gaps = biblelinks.wardrobeGaps(b, sp)
    out.append(_("Wardrobe gaps (a character in a scene with no wardrobe): %d.") % len(gaps))

    for scene, cid in gaps:
        c = b.get(cid)
        out.append("  " + _("scene %s: %s") % (scene, c.name if c else cid))

    noSet = [n for n, _f, _l in scenes if not biblelinks.itemsInScene(b, n).get("set")]
    out.append(_("Scenes with no set: %d%s") % (
        len(noSet), (" (" + ", ".join(noSet) + ")") if noSet else "") + ".")

    return "\n".join(out) + "\n"
