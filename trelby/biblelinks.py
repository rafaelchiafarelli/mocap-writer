# the script's links to the bible (film-bible/links), no wx: scene <-> set
# from the scene headings (links/1), props from capitalized words in
# Action (links/2), wardrobe <-> character x scene (links/3), copying items
# inside a film and to another film (links/4). nothing is created or
# linked without the creator: each scan returns a plan, and the panel shows
# it before anything is applied.

import os
import re
import shutil
import unicodedata

import mocap_contracts as mc

import trelby.bible as bible
import trelby.propwords as propwords
import trelby.scenenumbers as scenenumbers
import trelby.screenplay as screenplay

# a heading's prefix: INT., EXT., INT./EXT., I/E., EST. and their variants
PREFIX_RE = re.compile(
    r"^\s*(INT\.?\s*/\s*EXT|EXT\.?\s*/\s*INT|INT|EXT|EST|I\s*/\s*E)\.?\s+", re.IGNORECASE
)


# the location of a scene heading: without its INT./EXT. prefix and its
# time of day ("INT. SALA DE JANTAR - NOITE" -> "SALA DE JANTAR")
def locationOf(heading):
    s = PREFIX_RE.sub("", heading.strip())

    if " - " in s:
        s = s.rsplit(" - ", 1)[0]

    return s.strip(" .-")


# a name as compared: case, accents and spaces don't matter
def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()

    return " ".join(s.casefold().split())


# the item of map_ named name (or one of its aliases), or None
def findItem(b, map_, name):
    key = norm(name)

    for it in b.items.values():
        if it.map == map_ and (
            norm(it.name) == key or key in [norm(a) for a in it.msg.aliases]
        ):
            return it

    return None


# the scenes of sp: [(scene number, first line, last line of the scene)];
# scenes with no number yet are left out (save gives them one)
def scenesWithLines(sp):
    heads = scenenumbers.scenesOf(sp)
    out = []

    for i, (line, num) in enumerate(heads):
        end = heads[i + 1][0] - 1 if i + 1 < len(heads) else len(sp.lines) - 1

        if num:
            out.append((num, line, end))

    return out


# the number of the scene holding line, or None (before the first scene, or
# a scene with no number yet)
def sceneAt(sp, line):
    num = None

    for l, n in scenenumbers.scenesOf(sp):
        if l > line:
            break

        num = n

    return num


# the items linked to scene, by map: {map: [Item]}, each list by name
def itemsInScene(b, scene):
    out = {}

    for it in b.items.values():
        if scene in b.scenes(it):
            out.setdefault(it.map, []).append(it)

    for items in out.values():
        items.sort(key=lambda it: it.name.lower())

    return out


def elemText(sp, line):
    last = sp.getElemLastIndexFromLine(line)

    return " ".join(sp.lines[i].text for i in range(line, last + 1))


# links/1: what the scene headings say. returns (links, unknown): links is
# [(set item, scene)] for known locations not linked yet; unknown is
# {location: [scenes]} for locations no set is named after
def setPlan(b, sp):
    links = []
    unknown = {}

    for num, line, _end in scenesWithLines(sp):
        loc = locationOf(elemText(sp, line))

        if not loc:
            continue

        it = findItem(b, "set", loc)

        if it is None:
            for key in unknown:
                if norm(key) == norm(loc):
                    loc = key

            unknown.setdefault(loc, []).append(num)
        elif num not in {l.scene for l in it.msg.links}:
            links.append((it, num))

    return (links, unknown)


# make a set for each location in locations ({location: [scenes]}) and link
# its scenes; the name is the location as the script writes it
def createSets(b, locations, by="creator"):
    made = []

    for loc, nums in locations.items():
        it = b.create("set", loc, None, by)

        for n in nums:
            b.link(it, n, None, by)

        made.append(it)

    return made


def applyLinks(b, links, by="creator"):
    for it, num in links:
        b.link(it, num, None, by)


# the name a Character element speaks as: no extension ("ANA (V.O.)",
# "ANA (CONT'D)") and no dual-dialogue "^"
def speaker(text):
    return re.sub(r"\(.*?\)", "", text).strip().rstrip("^").strip()


# the names of the characters who speak in sp, normalized
def characterNames(sp):
    names = set()

    for i, l in enumerate(sp.lines):
        if l.lt == screenplay.CHARACTER and sp.isFirstLineOfElem(i):
            names.add(norm(speaker(l.text)))

    return names


# links/5: the speakers of sp's numbered scenes. returns (links, new):
# links is [(character item, scene)] for known characters not linked to
# that scene yet; new is {name: [scenes]} for names the bible does not
# know, as the script first writes them
def characterPlan(b, sp):
    links = []
    new = {}

    for num, first, last in scenesWithLines(sp):
        for i in range(first, last + 1):
            l = sp.lines[i]

            if l.lt != screenplay.CHARACTER or not sp.isFirstLineOfElem(i):
                continue

            name = speaker(l.text)

            if not name:
                continue

            it = findItem(b, "character", name)

            if it is None:
                for key in new:
                    if norm(key) == norm(name):
                        name = key

                if num not in new.setdefault(name, []):
                    new[name].append(num)
            elif num not in {x.scene for x in it.msg.links} and (it, num) not in links:
                links.append((it, num))

    return (links, new)


# make a character for each name and link its scenes
def createCharacters(b, names, by="creator"):
    made = []

    for name, nums in names.items():
        it = b.create("character", name, None, by)

        for n in nums:
            b.link(it, n, None, by)

        made.append(it)

    return made


# a prop as compared: also without a plural "s" on its words ("XÍCARAS
# AZUL" is "XÍCARA AZUL")
def propKey(run):
    return " ".join(
        w[:-1] if w.endswith("s") and len(w) > 3 else w for w in norm(run).split()
    )


def findProp(b, word):
    key = propKey(word)

    for it in b.items.values():
        if it.map == "prop" and key in [propKey(n) for n in [it.name, *it.msg.aliases]]:
            return it

    return None


# links/2: the props in the Action lines of sp. returns (links, new):
# links is [(prop item, scene)] for known props not linked yet; new is
# {run: [scenes]} for runs that are no character, no known prop and not
# marked "not a prop". the run being typed (cursorLine, cursorCol) is left
# out until it is finished.
def propPlan(b, sp, cursorLine=None, cursorCol=None):
    chars = characterNames(sp) | {
        norm(n) for it in b.items.values() if it.map == "character"
        for n in [it.name, *it.msg.aliases]
    }
    notProps = {propKey(w) for w in b.notProps}
    links = []
    new = {}

    for num, first, last in scenesWithLines(sp):
        for i in range(first, last + 1):
            l = sp.lines[i]

            if l.lt != screenplay.ACTION:
                continue

            typing = cursorCol if i == cursorLine else None

            for _s, _e, run in propwords.find_prop_words(l.text, typing):
                if norm(run) in chars or propKey(run) in notProps:
                    continue

                it = findProp(b, run)

                if it is None:
                    for key in new:
                        if propKey(key) == propKey(run):
                            run = key

                    if num not in new.setdefault(run, []):
                        new[run].append(num)
                elif num not in {l.scene for l in it.msg.links} and (it, num) not in links:
                    links.append((it, num))

    return (links, new)


# make a prop for each run (state script-stated, its first scene as the
# source) and link its scenes
def createProps(b, runs, by="creator"):
    made = []

    for run, nums in runs.items():
        it = b.create("prop", run, None, by)

        for n in nums:
            b.link(it, n, None, by)

        made.append(it)

    return made


# mark words "not a prop" for the whole film
def markNotProps(b, words, by="creator"):
    for w in words:
        if propKey(w) not in {propKey(x) for x in b.notProps}:
            b.notProps.append(w)

    b.saveNotProps(by)


# links/3: the characters in each scene of sp ({scene: {character id}}),
# the ones the bible knows by name or alias
def charactersByScene(b, sp):
    out = {}

    for num, first, last in scenesWithLines(sp):
        for i in range(first, last + 1):
            l = sp.lines[i]

            if l.lt == screenplay.CHARACTER and sp.isFirstLineOfElem(i):
                it = findItem(b, "character", speaker(l.text))

                if it:
                    out.setdefault(num, set()).add(it.id)

    return out


# link a wardrobe item to (character, scene)
def linkWardrobe(b, wardrobe, character, scene, by="creator"):
    b.link(wardrobe, scene, character.id, by)


def unlinkWardrobe(b, wardrobe, character, scene, by="creator"):
    b.unlink(wardrobe, scene, character.id, by)


# the gaps: [(scene, character id)] of characters in a scene with no
# wardrobe linked to them there. a gap is not an error, only a list.
def wardrobeGaps(b, sp):
    worn = {
        (l.scene, l.item)
        for it in b.items.values()
        if it.map == "wardrobe"
        for l in it.msg.links
        if l.HasField("item")
    }
    gaps = []

    for num, chars in charactersByScene(b, sp).items():
        for c in sorted(chars):
            if (num, c) not in worn:
                gaps.append((num, c))

    return gaps


# links/4: copy item (and its children, files included) into the film of
# dst (a Bible, the same one or another film's), under parent (an Item of
# dst, same map) or at the top level. every copy gets a new id of dst's
# film and no scene links: a scene number names a scene only in its own
# film, and a copy is unlinked by default. per-scene values are dropped for
# the same reason; links to other items are dropped when copying to
# another film. returns the copy.
def copyItem(src, item, dst, parent=None, by="creator", name=None):
    sameFilm = os.path.realpath(src.film.root) == os.path.realpath(dst.film.root)
    msg = mc.BibleItem()
    msg.CopyFrom(item.msg)
    del msg.links[:]
    keep = []

    for v in msg.values:
        f = bible.cb.fields(item.map)[v.field]

        if v.HasField("scene") or (f.type == "link" and not sameFilm):
            continue

        keep.append(v)

    del msg.values[:]
    msg.values.extend(keep)

    copy = dst.create(item.map, name or item.name, parent, by)
    msg.id = copy.id
    msg.name = copy.name

    if parent is not None:
        msg.parent = parent.id
    else:
        msg.ClearField("parent")

    copy.msg = msg

    # the files of the item, not its child items' folders
    srcDir = src.film.root / item.folder
    childDirs = {
        os.path.basename(c.folder) for c in src.children(item.map, item.id)
    }

    for entry in sorted(srcDir.iterdir()):
        if entry.is_dir() and entry.name not in childDirs:
            dstDir = dst.film.root / copy.folder / entry.name
            dst.film.checkWrite(copy.folder + "/" + entry.name + "/x")
            shutil.copytree(entry, dstDir, dirs_exist_ok=True)

    dst.save(copy, by)

    for child in src.children(item.map, item.id):
        copyItem(src, child, dst, copy, by)

    return copy


# the scenes that use item, so that removing it or placing a copy can warn
# the creator with them
def usedIn(b, item):
    return sorted(b.scenes(item), key=lambda n: scenenumbers.key(n) or (999999, n))
