# the scene index (preprod-link/contract/1), no wx: one entry per numbered
# scene of the script, built by code only from the script and the bible's
# existing records, written as the film's `bible/scene-index.json` (a
# mocap-contracts SceneIndex) for the mocap-preprod agents. nothing is
# inferred beyond the script's text and the links already made.

import hashlib
import re

import mocap_contracts as mc

import trelby.biblelinks as biblelinks
import trelby.fountain as fountain
import trelby.propwords as propwords
import trelby.screenplay as screenplay

# the index's path in the film's bible part
FILE = "scene-index.json"

ON = mc.Flag.Value("FLAG_ON")
OFF = mc.Flag.Value("FLAG_OFF")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# a heading's parts as written: ("INT.", "SALA DE JANTAR", "NOITE"); the
# prefix and the time of day are empty when the heading has none
def headingParts(heading):
    h = heading.strip()
    m = biblelinks.PREFIX_RE.match(h)
    prefix = m.group(0).strip() if m else ""
    rest = h[m.end():] if m else h
    tod = ""

    if " - " in rest:
        rest, tod = rest.rsplit(" - ", 1)

    return (prefix, rest.strip(" .-"), tod.strip())


# the text of the scene from first to last line, its elements as Fountain
# joins them: one element per line, a blank line between elements
def sceneText(sp, first, last):
    out = []
    i = first

    while i <= last:
        end = min(sp.getElemLastIndexFromLine(i), last)
        out.append(" ".join(sp.lines[j].text for j in range(i, end + 1)))
        i = end + 1

    return "\n\n".join(out) + "\n"


# the words of name found as whole words in text, case and accents ignored
def _named(name, text):
    key = biblelinks.norm(name)

    return bool(key) and re.search(r"(?<!\w)" + re.escape(key) + r"(?!\w)", text) is not None


# the set an entry names: of the sets linked to the scene, the one named
# like the heading's location, else the first by name
def _setOf(b, scene, location):
    sets = sorted(
        (it for it in b.items.values() if it.map == "set"
         and scene in [l.scene for l in it.msg.links]),
        key=lambda it: (it.name.lower(), it.id),
    )

    for it in sets:
        if biblelinks.norm(it.name) == biblelinks.norm(location):
            return it

    return sets[0] if sets else None


# one SceneEntry for the scene num, lines first..last, order n
def entry(b, sp, num, first, last, n, speakers):
    prefix, location, tod = headingParts(
        " ".join(sp.lines[j].text for j in range(first, sp.getElemLastIndexFromLine(first) + 1))
    )
    e = mc.SceneEntry(
        scene=num, order=n, int_ext=prefix, location=location, time_of_day=tod,
        first_page=max(sp.line2page(first), 1), last_page=max(sp.line2page(last), 1),
        first_line=first + 1, last_line=last + 1,
        text_hash=sha(sceneText(sp, first, last)),
    )
    st = _setOf(b, num, location) if b is not None else None

    if st:
        e.set_id = st.id

    seen = set()
    action = []

    for i in range(first, last + 1):
        l = sp.lines[i]

        if l.lt == screenplay.CHARACTER and sp.isFirstLineOfElem(i):
            name = biblelinks.speaker(l.text)

            if name and biblelinks.norm(name) not in seen:
                seen.add(biblelinks.norm(name))
                c = e.characters.add(name=name, speaks=ON)
                it = biblelinks.findItem(b, "character", name) if b is not None else None

                if it:
                    c.id = it.id
        elif l.lt == screenplay.ACTION:
            action.append(l.text)

    text = biblelinks.norm(" ".join(action))

    # named in Action: the bible's characters (name or alias) and the
    # script's speakers, as whole words
    named = []

    if b is not None:
        for it in sorted(b.items.values(), key=lambda it: (it.name.lower(), it.id)):
            if it.map == "character" and biblelinks.norm(it.name) not in seen:
                hit = next((n for n in [it.name, *it.msg.aliases] if _named(n, text)), None)

                if hit:
                    named.append((it.name, it.id))
                    seen.add(biblelinks.norm(it.name))

    for name in speakers:
        if biblelinks.norm(name) not in seen and _named(name, text):
            named.append((name, None))
            seen.add(biblelinks.norm(name))

    for name, rid in named:
        c = e.characters.add(name=name, speaks=OFF)

        if rid:
            c.id = rid

    # prop words: the runs of capitals in Action that are no character and
    # not marked "not a prop", as Find props reads them
    chars = {biblelinks.norm(n) for n in speakers} | seen
    notProps = {biblelinks.propKey(w) for w in b.notProps} if b is not None else set()
    props = set()

    for t in action:
        for _s, _e, run in propwords.find_prop_words(t, None):
            key = biblelinks.propKey(run)

            if biblelinks.norm(run) in chars or key in notProps or key in props:
                continue

            props.add(key)
            p = e.props.add(word=run)
            it = biblelinks.findProp(b, run) if b is not None else None

            if it:
                p.id = it.id

    return e


# the SceneIndex of sp with the bible b (None: no ids)
def build(sp, b):
    sp.paginate()
    speakers = []

    for i, l in enumerate(sp.lines):
        if l.lt == screenplay.CHARACTER and sp.isFirstLineOfElem(i):
            name = biblelinks.speaker(l.text)

            if name and biblelinks.norm(name) not in [biblelinks.norm(s) for s in speakers]:
                speakers.append(name)

    idx = mc.SceneIndex(script_hash=sha(fountain.generate(sp).text))

    for n, (num, first, last) in enumerate(biblelinks.scenesWithLines(sp), 1):
        idx.scenes.append(entry(b, sp, num, first, last, n, speakers))

    return idx


# the index's path relative to the film root, or None without a bible part
def path(film):
    p = film.part("bible")

    return p.path.rstrip("/") + "/" + FILE if p else None


# write the index of sp into the film; returns its text
def write(film, b, sp):
    text = mc.to_json(build(sp, b))
    film.writeText(path(film), text, "writer")

    return text
