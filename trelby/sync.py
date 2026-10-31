# Sync to spec (preprod-link/sync), no wx: the scene index of the script
# now against the last accepted one. a run writes the change set and
# changes nothing else; the snapshot advances only when the creator accepts,
# so a run not accepted can be repeated and gives the same changes.
#
#   <bible part>/sync/last-sync.json        the last accepted SceneIndex
#   <bible part>/sync/<time>-changes.json   one ChangeSet per run
#   <bible part>/scene-index.json           the accepted index, for the agents

import mocap_contracts as mc

import trelby.changeset as changeset
import trelby.sceneindex as sceneindex

LAST = "last-sync.json"


def syncDir(film):
    p = film.part("bible")

    return p.path.rstrip("/") + "/sync/" if p else None


# the last accepted SceneIndex, or None (no sync accepted yet)
def lastIndex(film):
    rel = syncDir(film) + LAST

    if not (film.root / rel).exists():
        return None

    return mc.from_json(mc.SceneIndex, film.readText(rel))


class Run:
    def __init__(self, index, changes, rel):
        # the SceneIndex now
        self.index = index

        # its ChangeSet against the last accepted index
        self.changes = changes

        # where the change set was written, relative to the film root
        self.rel = rel


# build the index of sp, diff it against the last accepted one and write
# the change set; nothing else is written
def run(film, b, sp, time=None):
    if syncDir(film) is None:
        raise ValueError(_("The film has no bible part to sync into."))

    idx = sceneindex.build(sp, b)
    cs = changeset.diff(lastIndex(film), idx, time)
    stamp = cs.time.replace("-", "").replace(":", "")
    rel = syncDir(film) + stamp + "-changes.json"
    film.writeText(rel, mc.to_json(cs), "writer")

    return Run(idx, cs, rel)


# the creator accepts the run: its index becomes the snapshot and the
# agents' scene index
def accept(film, r):
    text = mc.to_json(r.index)
    film.writeText(syncDir(film) + LAST, text, "writer")
    film.writeText(sceneindex.path(film), text, "writer")
