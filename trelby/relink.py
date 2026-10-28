# missing files of a film: search and relink (file-format/layout/3). no wx.
#
# a Ref is one reference to a file or folder that was not found where the
# film expects it. when the creator finds one somewhere else in the film
# root, the part of its path that changed is a pattern (e.g. "old/" ->
# "archive/old/"), tried on every other missing reference; what it finds is
# only suggested, and nothing is written until the creator accepts.

import os
from pathlib import Path

from mocap_contracts import film as cf

# the kinds of file a reference can expect, by extension; "folder" is a
# directory, "file" any file
KINDS = {
    "fountain": (".fountain",),
    "json": (".json",),
    "image": (".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff", ".bmp"),
    "blend": (".blend",),
}


class Ref:
    # what: shown to the creator; rel: where it was expected, relative to the
    # film root; kind: a key of KINDS, "folder" or "file"; apply(newRel):
    # saves the new path where the reference lives
    def __init__(self, what, rel, kind, apply):
        self.what = what
        self.rel = rel
        self.kind = kind
        self.apply = apply

    def __repr__(self):
        return "Ref(%r, %r, %r)" % (self.what, self.rel, self.kind)


# the kind a path needs to be, as text for the creator
def kindName(kind):
    if kind == "folder":
        return _("a folder")

    if kind == "file":
        return _("a file")

    return _("a file ending in %s") % ", ".join(KINDS[kind])


# True if the file or folder at path is of kind
def kindOk(kind, path):
    path = Path(path)

    if kind == "folder":
        return path.is_dir()

    if not path.is_file():
        return False

    if kind == "file":
        return True

    return path.suffix.lower() in KINDS[kind]


# path (absolute) as a film path relative to root, or None if it is not
# inside root or would not be a valid film path
def relativeIn(root, path):
    try:
        rel = Path(os.path.realpath(path)).relative_to(os.path.realpath(root))
    except ValueError:
        return None

    rel = rel.as_posix()

    if rel == "." or cf.path_problem(rel):
        return None

    return rel


# the pattern that turned oldRel into newRel: (old prefix, new prefix), the
# segments before the part both paths end with. "a/b/x.png" found at
# "c/b/x.png" -> ("a", "c"); a renamed file keeps only its folders' change.
def pattern(oldRel, newRel):
    old = list(cf.segments(oldRel))
    new = list(cf.segments(newRel))

    if old[-1:] != new[-1:]:
        old, new = old[:-1], new[:-1]

    while old and new and old[-1] == new[-1]:
        old.pop()
        new.pop()

    return ("/".join(old), "/".join(new))


# rel moved by pat, or None if pat does not apply to rel
def applyPattern(pat, rel):
    oldPrefix, newPrefix = pat
    segs = list(cf.segments(rel))
    pre = list(cf.segments(oldPrefix)) if oldPrefix else []

    if segs[: len(pre)] != pre:
        return None

    moved = (newPrefix.split("/") if newPrefix else []) + segs[len(pre) :]

    if not moved:
        return None

    out = "/".join(moved)

    if rel.endswith("/"):
        out += "/"

    return out


# [(ref, newRel)]: the refs pat finds at a path that exists in root and is
# of the right kind
def suggest(root, pat, refs):
    found = []

    for ref in refs:
        newRel = applyPattern(pat, ref.rel)

        if (
            newRel
            and newRel != ref.rel
            and not cf.path_problem(newRel)
            and kindOk(ref.kind, Path(root) / newRel)
        ):
            found.append((ref, newRel))

    return found


# check a file the creator picked for ref: (newRel, None), or (None, why)
def check(root, ref, path):
    rel = relativeIn(root, path)

    if rel is None:
        return (None, _("It must be inside the film folder %s.") % root)

    if not kindOk(ref.kind, path):
        return (None, _("It must be %s.") % kindName(ref.kind))

    if ref.kind == "folder":
        rel += "/"

    return (rel, None)
