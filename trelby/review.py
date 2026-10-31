# the review queue (preprod-link/review/1), no wx: every bible value in
# state proposal or TBD, and every value the latest sync lists as needs
# review, grouped by scene (an item-level value under its item, with the
# scenes it applies to, so it is decided once). the creator approves,
# rejects or edits them one at a time or in a batch; each item is written
# once per batch.

import mocap_contracts as mc

import trelby.bible as bible
import trelby.bibleedit as bibleedit
import trelby.sync as sync

# why a value is in the queue
PROPOSAL = "proposal"
TBD = "tbd"
REVIEW = "needs review"


class Entry:
    def __init__(self, item, value, why):
        self.item = item
        self.value = value
        self.why = why

    @property
    def scene(self):
        return self.value.scene if self.value.HasField("scene") else None


# the latest change set of the film's syncs, or None
def latestChanges(film):
    d = sync.syncDir(film)

    if d is None or not (film.root / d).is_dir():
        return None

    runs = sorted((film.root / d).glob("*-changes.json"))

    if not runs:
        return None

    return mc.from_json(mc.ChangeSet, runs[-1].read_text(encoding="utf-8"))


def _sortKey(e):
    return (e.scene is None, bibleedit.scenenumbers.key(e.scene) or (999999, e.scene or ""),
            e.item.name.lower(), e.item.id, e.value.field)


# the queue: per scene (item-level values last), then item and field. a
# value listed for two reasons appears once, as a proposal or TBD
def queue(b, changes=None):
    out = []
    seen = set()

    for it in b.items.values():
        for v in it.msg.values:
            st = bible.stateName(v.state)

            if st in (PROPOSAL, TBD):
                out.append(Entry(it, v, st))
                seen.add((it.id, v.SerializeToString()))

    if changes is not None:
        for a in sync.affected(b, changes):
            key = (a.item.id, a.value.SerializeToString())

            if key not in seen:
                out.append(Entry(a.item, a.value, REVIEW))
                seen.add(key)

    return sorted(out, key=_sortKey)


# the scenes an entry applies to: its own, or all of its item's
def appliesTo(b, e):
    return [e.scene] if e.scene else sorted(
        b.scenes(e.item), key=lambda n: bibleedit.scenenumbers.key(n) or (999999, n)
    )


def valueText(v):
    return v.text or (v.number + (" " + v.unit if v.unit else ""))


# write each item of entries once, putting it back if the contract refuses
def _apply(b, entries, change):
    byItem = {}

    for e in entries:
        byItem.setdefault(e.item.id, (e.item, []))[1].append(e)

    for item, es in byItem.values():
        before = item.msg.SerializeToString()

        for e in es:
            change(item, e)

        try:
            b.save(item, "creator")
        except mc.ContractError:
            item.msg.ParseFromString(before)

            raise


# approve: creator-approved, the source kept; a needs-review value keeps
# its state (it was looked at)
def approve(b, entries):
    def change(item, e):
        if e.why != REVIEW:
            e.value.state = bible.state("creator-approved")
            e.value.ClearField("revisit")

    _apply(b, [e for e in entries if e.why != REVIEW], change)


# the values of field in scene that a proposal replaced: from the change
# log, the newest write of the item that brought the proposal in, its
# before; [] when there was none (or the log does not have it)
def previous(b, item, value):
    scene = value.scene if value.HasField("scene") else None

    def same(v):
        return v.field == value.field and (v.scene if v.HasField("scene") else None) == scene

    for c in reversed(b.film.changes()):
        if c.record != item.id or not c.HasField("after"):
            continue

        after = mc.from_json(mc.BibleItem, c.after)

        if value not in list(after.values):
            continue

        before = mc.from_json(mc.BibleItem, c.before) if c.HasField("before") else None
        old = [v for v in before.values if same(v)] if before else []

        if value not in old:
            return old

    return []


# reject: the value is removed and the value it replaced (from the change
# log) comes back
def reject(b, entries):
    prev = {id(e): previous(b, e.item, e.value) for e in entries}

    def change(item, e):
        for i, v in enumerate(item.msg.values):
            if v == e.value:
                del item.msg.values[i]
                break

        for v in prev[id(e)]:
            if v not in list(item.msg.values):
                item.msg.values.add().CopyFrom(v)

    _apply(b, entries, change)


# edit: the creator's text replaces the value, creator-approved
def edit(b, e, text):
    f = bibleedit.field(e.item.map, e.value.field)
    new = bibleedit.parse(f, text)

    def change(item, e):
        if f.type == "number":
            e.value.number, unit = new[0] if new else ("", None)

            if unit:
                e.value.unit = unit
        else:
            e.value.text = new[0] if new else ""

        e.value.state = bible.state("creator-approved")
        e.value.source = bibleedit.creatorSource()
        e.value.by = "creator"
        e.value.ClearField("revisit")

    _apply(b, [e], change)
