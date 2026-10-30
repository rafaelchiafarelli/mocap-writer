# annotations on the script (fountain-native/notes/1): notes and scene
# annotations kept as records in the film's `annotations` part, never in
# the Fountain text. each record is anchored by its scene number, the
# element's index in the scene (the heading is 0; none: the whole scene)
# and the quoted text with its occurrence (none: the whole element). no wx.
#
# anchors follow the text: every time the script is resolved, each anchor
# is found again, its quote first in its element, then anywhere in its
# scene, then as the closest text in its element (the quote edited); a
# quote that is gone moves the annotation to its whole element, an element
# that is gone moves it to its scene, and a scene that is gone leaves it on
# its number, which the save turns into the scene's OMITTED heading. on
# open (the script may have been edited in another tool), a quote not found
# is not moved: the annotation stays in its scene and is listed as
# unattached, to re-attach by hand. an annotation is never deleted but by
# the creator. the anchors changed are written when the script is saved.

import difflib

import mocap_contracts as mc
from mocap_contracts import annotation as ca

import trelby.config as config
import trelby.scenenumbers as scenenumbers
import trelby.screenplay as screenplay

KINDS = ca.KINDS

KIND_LABELS = {
    "note": "Note",
    "character_direction": "Character direction",
    "prop_direction": "Prop direction",
    "special_effect": "Special effect",
    "set_direction": "Set direction",
    "sound_direction": "Sound direction",
    "general_direction": "General direction",
    "transition": "Transition",
    "shot": "Shot",
}

# how close an edited quote must still be to be followed (difflib ratio)
FOLLOW_RATIO = 0.6


class Element:
    def __init__(self, first, last, text, offsets):
        # first and last line of the element
        self.first = first
        self.last = last

        # the element's text, lines joined as Fountain joins them
        self.text = text

        # [(line, offset of the line's first character in text)]
        self.offsets = offsets

    # [(line, startCol, endCol)] covering text[start:end]; endCol exclusive
    def spans(self, start, end):
        out = []

        for k, (line, off) in enumerate(self.offsets):
            nextOff = self.offsets[k + 1][1] if k + 1 < len(self.offsets) else len(self.text) + 1
            lo = max(start, off)
            hi = min(end, nextOff)

            if lo < hi:
                out.append((line, lo - off, hi - off))

        return out


# the elements of each numbered scene of sp: {number: [Element]}, the
# heading being element 0
def sceneElements(sp):
    ls = sp.lines
    heads = scenenumbers.scenesOf(sp)
    out = {}

    for k, (head, num) in enumerate(heads):
        if not num:
            continue

        end = heads[k + 1][0] if k + 1 < len(heads) else len(ls)
        elems = []
        i = head

        while i < end:
            last = sp.getElemLastIndexFromLine(i)
            text = ""
            offsets = []

            for j in range(i, last + 1):
                offsets.append((j, len(text)))
                text += ls[j].text

                if j != last:
                    text += config.lb2str(ls[j].lb)

            elems.append(Element(i, last, text, offsets))
            i = last + 1

        out[num] = elems

    return out


# where an annotation is in the script now
class Place:
    def __init__(self, spans, line, attached=True, why=""):
        # [(line, startCol, endCol)] of its quote, or of its whole element,
        # or [] for a whole scene
        self.spans = spans

        # the line its mark goes on: the element's first line, or the
        # scene's heading
        self.line = line

        # False when it could not be placed (listed as unattached)
        self.attached = attached
        self.why = why


def _find(text, quote, occurrence):
    at = -1

    for _i in range(max(occurrence, 1)):
        at = text.find(quote, at + 1)

        if at == -1:
            return -1

    return at


def _occurrenceAt(text, quote, at):
    n = 0
    i = text.find(quote)

    while i != -1 and i <= at:
        n += 1
        i = text.find(quote, i + 1)

    return max(n, 1)


# the closest substring of text to quote, as (start, end), or None
def _closest(text, quote):
    if not quote or not text:
        return None

    sm = difflib.SequenceMatcher(None, text, quote, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size]

    if not blocks:
        return None

    start = blocks[0].a - blocks[0].b
    end = blocks[-1].a + (len(quote) - blocks[-1].b)
    start, end = max(start, 0), min(end, len(text))

    if difflib.SequenceMatcher(None, text[start:end], quote).ratio() < FOLLOW_RATIO:
        return None

    return (start, end)


class Annotations:
    def __init__(self, film):
        self.film = film

        # id -> mc.Annotation
        self.records = {}

        # the ids whose record changed since the last write
        self.dirty = set()

        # id -> (the text of its element, the number of elements in its
        # scene) when last placed, to follow the element when others are
        # inserted before it
        self.elemTexts = {}

        self.load()

    def base(self):
        p = self.film.part("annotations")

        return p.path.rstrip("/") if p else None

    def rel(self, rid):
        return self.base() + "/" + ca.file_name(rid)

    def load(self):
        self.records = {}
        base = self.base()

        if base is None or not (self.film.root / base).is_dir():
            return

        for path in sorted((self.film.root / base).glob("annotation-*.json")):
            rel = base + "/" + path.name

            try:
                a = mc.from_json(mc.Annotation, path.read_text(encoding="utf-8"))
            except mc.ContractError as e:
                self.film.problem(_("Annotation"), rel, str(e))

                continue

            if ca.file_name(a.id) != path.name:
                self.film.problem(_("Annotation"), rel, _("its id is %s") % a.id)

                continue

            self.records[a.id] = a

    def kind(self, a):
        return ca.kind_word(a.kind)

    # a new annotation of kind on the anchor (scene, element, quote); a
    # shot gets the next number of its scene
    def add(self, kind, scene, element=None, quote=None, occurrence=None, text="", by="creator"):
        a = mc.Annotation(
            id=self.film.newId("annotation"),
            kind=ca.kind_value(kind),
            by=by,
        )
        a.anchor.scene = scene

        if element is not None:
            a.anchor.element = element

        if quote:
            a.anchor.quote = quote
            a.anchor.occurrence = occurrence or 1

        if text:
            a.text = text

        if kind == "shot":
            a.shot = self.nextShot(scene)

        self.save(a, by)
        self.records[a.id] = a

        return a

    # the next shot number of scene, saved before it is used, so a number
    # never comes back
    def nextShot(self, scene):
        rel = self.base() + "/" + ca.SHOT_COUNTERS_FILE

        if (self.film.root / rel).exists():
            c = mc.from_json(mc.ShotCounters, self.film.readText(rel))
        else:
            c = mc.ShotCounters()

        n = c.next.get(scene, 1)
        c.next[scene] = n + 1
        self.film.writeText(rel, mc.to_json(c))

        return n

    def save(self, a, by=None):
        self.film.writeText(self.rel(a.id), mc.to_json(a), by)
        self.dirty.discard(a.id)

    def delete(self, rid, by="creator"):
        self.film.deleteFile(self.rel(rid), by)
        del self.records[rid]
        self.dirty.discard(rid)

    # write the anchors that moved since the last write
    def flush(self, by="writer"):
        for rid in sorted(self.dirty):
            if rid in self.records:
                self.save(self.records[rid], by)

        self.dirty = set()

    # place every annotation in sp: {id: Place}. editing=False is the first
    # placement after the script was opened: a quote not found is then
    # listed as unattached instead of being moved to its element.
    def resolve(self, sp, editing=True):
        scenes = sceneElements(sp)
        heads = {n: l for l, n in scenenumbers.scenesOf(sp) if n}
        out = {}

        for rid, a in self.records.items():
            out[rid] = self.place(a, scenes, heads, editing)

        return out

    def place(self, a, scenes, heads, editing):
        anc = a.anchor
        elems = scenes.get(anc.scene)

        if elems is None:
            return Place([], None, False, _("scene %s is not in the script") % anc.scene)

        head = heads[anc.scene]

        if not anc.HasField("element"):
            return Place([], head)

        e = self.followElement(a, elems)

        if e is None:
            # the element is gone: the annotation moves to its scene
            if editing:
                anc.ClearField("element")
                anc.ClearField("quote")
                anc.ClearField("occurrence")
                self.dirty.add(a.id)

            return Place([], head, editing, "" if editing else _("its element is gone"))

        el = elems[e]

        if not anc.HasField("quote"):
            self.elemTexts[a.id] = (el.text, len(elems))

            return Place(el.spans(0, len(el.text)), el.first)

        q, occ = anc.quote, anc.occurrence or 1
        at = _find(el.text, q, occ)

        if at == -1:
            # the quote moved to another element of the scene
            for k, other in enumerate(elems):
                at = _find(other.text, q, 1)

                if at != -1:
                    e, el = k, other
                    anc.element = k
                    anc.occurrence = _occurrenceAt(other.text, q, at)
                    self.dirty.add(a.id)

                    break

        if at == -1 and editing:
            # the quote was edited: follow the closest text
            se = _closest(el.text, q)

            if se is not None:
                at = se[0]
                anc.quote = el.text[se[0] : se[1]]
                anc.occurrence = _occurrenceAt(el.text, anc.quote, at)
                q = anc.quote
                self.dirty.add(a.id)

        if at == -1:
            if not editing:
                return Place([], head, False, _("its text %r is not in the scene") % q)

            # the quote is gone: the annotation moves to its whole element
            anc.ClearField("quote")
            anc.ClearField("occurrence")
            self.dirty.add(a.id)
            self.elemTexts[a.id] = (el.text, len(elems))

            return Place(el.spans(0, len(el.text)), el.first)

        if anc.element != e:
            anc.element = e
            self.dirty.add(a.id)

        self.elemTexts[a.id] = (el.text, len(elems))

        return Place(el.spans(at, at + len(q)), el.first)

    # the index of a's element in elems now, or None if it is gone: the
    # same index while its text is unchanged or still holds the quote, else
    # the element of the scene closest to its last known text
    def followElement(self, a, elems):
        anc = a.anchor
        e = anc.element
        known = self.elemTexts.get(a.id)
        q = anc.quote if anc.HasField("quote") else None

        if e < len(elems) and (
            known is None
            or elems[e].text == known[0]
            or (q and q in elems[e].text)
            # no element came or went in the scene: the same index is the
            # same element, its text edited
            or len(elems) == known[1]
        ):
            return e

        if known is None:
            return None

        last = known[0]

        best, bestRatio = None, 0.5

        for k, el in enumerate(elems):
            r = difflib.SequenceMatcher(None, el.text, last).ratio()

            if r > bestRatio:
                best, bestRatio = k, r

        if best is not None and best != e:
            anc.element = best
            self.dirty.add(a.id)

        return best

    # the annotations at (line, col) of the script: those whose span holds
    # it, then those of its element, then of its scene
    def at(self, places, line, col=None):
        out = []

        for rid, p in places.items():
            if any(l == line and (col is None or c1 <= col < c2) for l, c1, c2 in p.spans):
                out.append(rid)

        return out

    # put the annotation at a new anchor (re-attaching it by hand)
    def move(self, rid, scene, element=None, quote=None, occurrence=None, by="creator"):
        a = self.records[rid]
        a.anchor.Clear()
        a.anchor.scene = scene

        if element is not None:
            a.anchor.element = element

        if quote:
            a.anchor.quote = quote
            a.anchor.occurrence = occurrence or 1

        self.elemTexts.pop(rid, None)
        self.save(a, by)

    # scenes renamed by a move or Renumber all (fountain-native/scenes/5)
    def renameScenes(self, moves, by="writer"):
        changed = []

        for a in self.records.values():
            if a.anchor.scene in moves:
                a.anchor.scene = moves[a.anchor.scene]
                changed.append(a)

        for a in changed:
            self.save(a, by)

        rel = self.base() + "/" + ca.SHOT_COUNTERS_FILE

        if (self.film.root / rel).exists():
            c = mc.from_json(mc.ShotCounters, self.film.readText(rel))
            old = dict(c.next)
            c.next.clear()

            for s, n in old.items():
                key = moves.get(s, s)
                c.next[key] = max(n, c.next.get(key, 1))

            if dict(c.next) != old:
                self.film.writeText(rel, mc.to_json(c), by)

        return changed

    # a short text for a tooltip or a list
    def describe(self, a):
        kind = _(KIND_LABELS[self.kind(a)])
        head = kind

        if a.HasField("shot"):
            head += " " + ca.shot_name(a.anchor.scene, a.shot)

        parts = [head]

        if a.HasField("text") and a.text:
            parts.append(a.text)

        fields = ca.fields(self.kind(a))

        for v in a.values:
            f = fields.get(v.field)
            value = v.number + " " + v.unit if v.HasField("number") else v.text
            parts.append("%s: %s" % (f.label if f else v.field, value))

        return "\n".join(parts)


# the anchor for a selection or the cursor in sp: (scene, element, quote,
# occurrence), or None when the cursor is before the first numbered scene.
# a selection inside one element anchors its text; anything else, the
# cursor's whole element.
def anchorAt(sp):
    scenes = sceneElements(sp)
    line = sp.line
    num = None

    for l, n in scenenumbers.scenesOf(sp):
        if l > line:
            break

        num = n

    if not num or num not in scenes:
        return None

    elems = scenes[num]
    k = next((i for i, el in enumerate(elems) if el.first <= line <= el.last), None)

    if k is None:
        return None

    el = elems[k]
    marked = sp.getMarkedLines()

    if marked and el.first <= marked[0] and marked[1] <= el.last:
        start = end = None

        for i in range(marked[0], marked[1] + 1):
            c1, c2 = sp.getMarkedColumns(i, marked)
            off = dict(el.offsets)[i]

            if start is None:
                start = off + c1

            end = off + c2 + 1

        quote = el.text[start:end]

        if quote.strip():
            return (num, k, quote, _occurrenceAt(el.text, quote, start))

    return (num, k, None, None)
