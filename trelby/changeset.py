# the change set between two scene indexes (preprod-link/contract/2), no wx:
# what changed in the script from the last accepted sync to now, scene by
# scene, as a mocap-contracts ChangeSet. scenes are matched by their
# number, never by heading or position.

import datetime

import mocap_contracts as mc

import trelby.biblelinks as biblelinks
import trelby.sceneindex as sceneindex


def _type(name):
    return mc.SceneChangeType.Value("SCENE_CHANGE_TYPE_" + name)


# the sha256 of an index as written
def indexHash(idx):
    return sceneindex.sha(mc.to_json(idx))


def heading(e):
    return " ".join(
        p for p in (e.int_ext, e.location + (" - " + e.time_of_day if e.time_of_day else "")) if p
    )


# the scenes of old that kept their place among the scenes both have: the
# longest run in the same order (the others moved)
def _kept(oldOrder, newOrder):
    common = [s for s in newOrder if s in oldOrder]
    pos = {s: i for i, s in enumerate(oldOrder)}
    seq = [pos[s] for s in common]

    # longest increasing subsequence, O(n^2): scripts have hundreds of scenes
    best = [1] * len(seq)
    prev = [-1] * len(seq)

    for i in range(len(seq)):
        for j in range(i):
            if seq[j] < seq[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
                prev[i] = j

    kept = set()
    i = max(range(len(seq)), key=lambda k: best[k]) if seq else -1

    while i >= 0:
        kept.add(common[i])
        i = prev[i]

    return kept


# {key: name} of an entry's characters or props, keyed by bible id when
# known, else by the name as compared
def _keyed(items, attr):
    return {(it.id if it.HasField("id") else biblelinks.norm(getattr(it, attr))): getattr(it, attr)
            for it in items}


# the ChangeSet from old (a SceneIndex, or None on a first sync) to new
def diff(old, new, time=None):
    time = time or (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    cs = mc.ChangeSet(time=time, to_hash=indexHash(new))
    olds = {e.scene: e for e in old.scenes} if old is not None else {}
    news = {e.scene: e for e in new.scenes}

    if old is not None:
        cs.from_hash = indexHash(old)

    def add(name, scene, before=None, after=None):
        c = cs.changes.add(type=_type(name), scene=scene)

        if before:
            c.old_value = before

        if after:
            c.new_value = after

    for e in old.scenes if old is not None else []:
        if e.scene not in news:
            add("SCENE_REMOVED", e.scene, heading(e))

    kept = _kept([e.scene for e in old.scenes], [e.scene for e in new.scenes]) if old else set()

    for e in new.scenes:
        o = olds.get(e.scene)

        if o is None:
            add("SCENE_ADDED", e.scene, None, heading(e))

            continue

        if e.scene not in kept:
            add("SCENE_MOVED", e.scene, str(o.order), str(e.order))

        if heading(o) != heading(e):
            add("HEADING_CHANGED", e.scene, heading(o), heading(e))

        if o.text_hash != e.text_hash:
            add("TEXT_CHANGED", e.scene)

        for what, attr, entered, left in (
            ("characters", "name", "CHARACTER_ENTERED", "CHARACTER_LEFT"),
            ("props", "word", "PROP_ADDED", "PROP_REMOVED"),
        ):
            a = _keyed(getattr(o, what), attr)
            b = _keyed(getattr(e, what), attr)

            for k in b:
                if k not in a:
                    add(entered, e.scene, None, b[k])

            for k in a:
                if k not in b:
                    add(left, e.scene, a[k])

        if o.set_id != e.set_id:
            add("SET_LINK_CHANGED", e.scene, o.set_id, e.set_id)

    return cs
