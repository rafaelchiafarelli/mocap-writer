# a film root (file-format/layout/1): film.json, the parts of the film and
# who owns each one, the id spaces and their counters. opening never breaks:
# a missing or invalid part or file is a Problem in film.problems and the
# rest of the film opens; only a missing or invalid film.json stops the open
# (FilmError). no wx.
#
# the format is the mocap-contracts film.harpia (third_party/mocap-contracts):
# every file is read and written through its from_json / to_json, so a file
# that breaks its message is never written and is refused on read.

import datetime
import json
import os
import tempfile
from pathlib import Path

import mocap_contracts as mc
from mocap_contracts import film as cf

import trelby.relink as relink

PROGRAM = "mocap-writer"

# the parts of a new film (layout/1, "Default parts")
DEFAULT_PARTS = (
    ("script", "script.fountain"),
    ("settings", "settings/script-settings.json"),
    ("bible", "bible/"),
    ("annotations", "annotations/"),
    ("history", "history/"),
)


# opening a film failed: no film.json, or one that breaks its message
class FilmError(Exception):
    pass


# a write to a file this program doesn't own, or outside every part
class OwnerError(Exception):
    pass


# something of the film that could not be opened: what it is, where it was
# expected (a path relative to the film root) and why; ref, a relink.Ref when
# the creator can search for it (layout/3)
class Problem:
    def __init__(self, what, where, why, ref=None):
        self.what = what
        self.where = where
        self.why = why
        self.ref = ref

    def __eq__(self, other):
        return (self.what, self.where, self.why) == (
            other.what,
            other.where,
            other.why,
        )

    def __repr__(self):
        return "Problem(%r, %r, %r)" % (self.what, self.where, self.why)


class Film:
    # use Film.open or Film.create. owner is who this program writes as:
    # "writer", or an agent's name.
    def __init__(self, root, index, owner):
        self.root = Path(root)
        self.index = index
        self.owner = owner

        # [Problem], filled on open and by the readers of each part
        self.problems = []

    # open the film at root and list what is missing or invalid in
    # self.problems. raises FilmError if film.json is missing or invalid.
    @classmethod
    def open(cls, root, owner=cf.WRITER):
        root = Path(root)
        index = _read(root / cf.FILM_FILE, mc.Film, FilmError)
        f = cls(root, index, owner)

        for p in index.parts:
            # a file part other than the script (settings) that is missing
            # was not written yet: its program uses defaults
            notYet = not p.path.endswith("/") and p.name != cf.SCRIPT_PART

            if not (root / p.path).exists() and not notYet:
                kind = _("folder") if p.path.endswith("/") else _("file")
                f.problem(
                    _("Part '%s'") % p.name,
                    p.path,
                    _("the %s is missing") % kind,
                    f.partRef(p),
                )

        for s in index.spaces:
            rel = cf.ids_file(s.code)

            if (root / rel).exists():
                try:
                    _read(root / rel, mc.IdCounters, mc.ContractError)
                except mc.ContractError as e:
                    f.problem(_("Id counters of '%s'") % s.code, rel, str(e))

            elif s.code == cf.WRITER_SPACE:
                f.problem(
                    _("Id counters of '%s'") % s.code,
                    rel,
                    _("the file is missing: no new record can get an id"),
                )

        return f

    # make a new film at root, a folder with no film.json yet: film.json
    # with the default parts and the writer's space, its counters and the
    # folder parts. scriptText, if given, becomes the script part. the
    # writer owns film.json, so only the writer creates a film.
    @classmethod
    def create(cls, root, scriptText=None):
        root = Path(root)

        if (root / cf.FILM_FILE).exists():
            raise FilmError(_("%s already holds a film.") % root)

        index = mc.Film(
            format_version=cf.FORMAT_VERSION,
            origin=_origin(),
            parts=[mc.FilmPart(name=n, path=p, owner=cf.WRITER) for n, p in DEFAULT_PARTS],
            spaces=[mc.IdSpace(code=cf.WRITER_SPACE, owner=cf.WRITER)],
        )

        root.mkdir(parents=True, exist_ok=True)
        f = cls(root, index, cf.WRITER)
        f.saveIndex()
        f.writeText(cf.ids_file(cf.WRITER_SPACE), mc.to_json(mc.IdCounters()))

        for p in index.parts:
            if p.path.endswith("/"):
                (root / p.path).mkdir(parents=True, exist_ok=True)

        if scriptText is not None:
            f.writeText(f.part("script").path, scriptText)

        return f

    def problem(self, what, where, why, ref=None):
        self.problems.append(Problem(what, where, why, ref))

    # the relink.Ref of part p: a new path is saved in film.json
    def partRef(self, p):
        if p.path.endswith("/"):
            kind = "folder"
        elif p.name == cf.SCRIPT_PART:
            kind = "fountain"
        elif p.path.endswith(".json"):
            kind = "json"
        else:
            kind = "file"

        name = p.name

        return relink.Ref(
            _("Part '%s'") % name,
            p.path,
            kind,
            lambda rel: self.setPartPath(name, rel),
        )

    # point the part named name at rel and save film.json; the contract
    # checks the new index before anything is written
    def setPartPath(self, name, rel):
        index = mc.Film()
        index.CopyFrom(self.index)

        for p in index.parts:
            if p.name == name:
                p.path = rel

        mc.to_json(index)
        self.index = index
        self.saveIndex()

    # add a part (import-to-film: `source`); a folder part's folder is made.
    # the contract checks the new index before it is saved
    def addPart(self, name, rel):
        index = mc.Film()
        index.CopyFrom(self.index)
        index.parts.add(name=name, path=rel, owner=cf.WRITER)
        mc.to_json(index)
        self.index = index
        self.saveIndex()

        if rel.endswith("/"):
            (self.root / rel).mkdir(parents=True, exist_ok=True)

    # the part named name, or None
    def part(self, name):
        for p in self.index.parts:
            if p.name == name:
                return p

        return None

    # absolute path of the part named name, or None
    def partPath(self, name):
        p = self.part(name)

        return self.root / p.path if p else None

    # the part holding rel (a path relative to the film root), or None.
    # parts never nest, so this is a prefix check by segment.
    def partOf(self, rel):
        segs = cf.segments(rel)

        for p in self.index.parts:
            ps = cf.segments(p.path)

            if segs[: len(ps)] == ps:
                return p

        return None

    # who owns the file at rel: the writer for film.json, a space's owner for
    # its counters, a part's owner for what is in it; None outside them all
    def ownerOf(self, rel):
        if rel == cf.FILM_FILE:
            return cf.WRITER

        segs = cf.segments(rel)

        if len(segs) == 2 and segs[0] == "ids":
            code = segs[1].removesuffix(".json")

            for s in self.index.spaces:
                if s.code == code:
                    return s.owner

            return None

        p = self.partOf(rel)

        return p.owner if p else None

    def owns(self, rel):
        return self.ownerOf(rel) == self.owner

    # raise OwnerError unless this program may write rel
    def checkWrite(self, rel):
        cf.check_path(rel)

        if not self.owns(rel):
            raise OwnerError(
                _("%s belongs to %s, not to %s.")
                % (rel, self.ownerOf(rel) or _("no part"), self.owner)
            )

    def readText(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    # the file's text, or None if there is none
    def textOrNone(self, rel):
        try:
            return self.readText(rel)
        except FileNotFoundError:
            return None

    # write text to rel, atomically (a crash leaves the old file or the new
    # one, never half of one). a record's change is logged (layout/5) as
    # made by by, default this program's owner.
    def writeText(self, rel, text, by=None):
        self.checkWrite(rel)
        before = self.textOrNone(rel) if self.logs(rel) else None
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")

        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fp:
                fp.write(text)

            os.replace(tmp, path)
        except BaseException:
            if os.path.exists(tmp):
                os.remove(tmp)

            raise

        if self.logs(rel) and before != text:
            self.log(rel, "UPDATE" if before is not None else "CREATE", before, text, by)

    def deleteFile(self, rel, by=None):
        self.checkWrite(rel)
        before = self.textOrNone(rel) if self.logs(rel) else None
        (self.root / rel).unlink()

        if before is not None:
            self.log(rel, "DELETE", before, None, by)

    # True if a write to rel goes into the change log: a text record in a
    # part other than the script and the history, when this program owns
    # the history. film.json and the id counters are bookkeeping, not
    # records.
    def logs(self, rel):
        p = self.partOf(rel)
        history = self.part("history")

        return bool(
            p
            and history
            and p.name not in ("history", cf.SCRIPT_PART)
            and self.owns(history.path)
            and not self.derived(rel)
        )

    # True for the files built from the script by code, never edited
    # (preprod-link): the scene index and the sync folder in the bible part
    def derived(self, rel):
        p = self.part("bible")

        if not p:
            return False

        base = p.path.rstrip("/") + "/"

        return rel == base + "scene-index.json" or rel.startswith(base + "sync/")

    # append one Change to history/<yyyy-mm>.jsonl
    def log(self, rel, op, before, after, by):
        time = (
            datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
        c = mc.Change(
            time=time,
            by=by or self.owner,
            path=rel,
            op=mc.ChangeOp.Value("CHANGE_OP_" + op),
        )
        record = _recordId(after if after is not None else before)

        if record:
            c.record = record

        if before is not None:
            c.before = before

        if after is not None:
            c.after = after

        line = json.dumps(json.loads(mc.to_json(c)), ensure_ascii=False)
        logRel = self.historyFile(time)
        path = self.root / logRel
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "a", encoding="utf-8", newline="") as fp:
            fp.write(line + "\n")

    # the log file of a change made at time, inside the history part
    def historyFile(self, time):
        default = cf.history_file(time)
        history = self.part("history").path

        return history + default.removeprefix("history/")

    # every logged Change, oldest first; only by's if by is given. a line
    # that breaks its message is a problem, not a crash.
    def changes(self, by=None):
        folder = self.partPath("history")
        out = []

        if folder is None or not folder.is_dir():
            return out

        for path in sorted(folder.glob("*.jsonl")):
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
                if not line.strip():
                    continue

                try:
                    c = mc.from_json(mc.Change, line)
                except mc.ContractError as e:
                    self.problem(_("Change log"), "%s:%d" % (path.name, i + 1), str(e))

                    continue

                if by is None or c.by == by:
                    out.append(c)

        return out

    # undo changes, newest first: each record goes back to its before (a
    # create is deleted). the undo is itself logged, as made by by.
    def revert(self, changes, by=None):
        for c in sorted(changes, key=lambda c: c.time, reverse=True):
            op = mc.ChangeOp.Name(c.op)

            if op == "CHANGE_OP_CREATE":
                if (self.root / c.path).exists():
                    self.deleteFile(c.path, by)
            else:
                self.writeText(c.path, c.before, by)

    # write film.json, with this program as its origin
    def saveIndex(self):
        self.index.origin.CopyFrom(_origin())
        self.writeText(cf.FILM_FILE, mc.to_json(self.index))

    # a new record id of kind in space (default: this program's first
    # space). the counter goes up and is saved before the id is returned, so
    # a crash leaves a gap, never a reused id.
    def newId(self, kind, space=None):
        if space is None:
            space = self.spaceOf(self.owner)

            if space is None:
                raise OwnerError(_("%s has no id space in this film.") % self.owner)

        rel = cf.ids_file(space)

        if (self.root / rel).exists():
            counters = _read(self.root / rel, mc.IdCounters, FilmError)
        elif space == cf.WRITER_SPACE:
            raise FilmError(
                _("%s is missing: new ids could repeat old ones.") % rel
            )
        else:
            counters = mc.IdCounters()

        n = counters.next.get(kind, 1)
        rid = cf.record_id(kind, space, n)
        counters.next[kind] = n + 1
        self.writeText(rel, mc.to_json(counters))

        return rid

    # the first space owned by owner, or None
    def spaceOf(self, owner):
        for s in self.index.spaces:
            if s.owner == owner:
                return s.code

        return None

    # add an agent's space, and with it, if path is given, its proposals
    # part. a writer action: film.json is the writer's.
    def addSpace(self, code, owner, path=None):
        spaces = list(self.index.spaces)
        spaces.append(mc.IdSpace(code=code, owner=owner))
        parts = list(self.index.parts)

        if path is not None:
            parts.append(
                mc.FilmPart(name=cf.PROPOSALS_PREFIX + code, path=path, owner=owner)
            )

        index = mc.Film()
        index.CopyFrom(self.index)
        del index.spaces[:]
        index.spaces.extend(spaces)
        del index.parts[:]
        index.parts.extend(parts)

        # check before anything changes: to_json raises on a broken rule
        mc.to_json(index)
        self.index = index
        self.saveIndex()


# the problems as text for the user, one line each
def problemsText(problems):
    lines = [_("The film opened, but some of it is missing or invalid:"), ""]

    for p in problems:
        lines.append("%s (%s): %s" % (p.what, p.where, p.why))

    return "\n".join(lines)


def _origin():
    from trelby import misc  # imports wx; only for the version

    return mc.FilmOrigin(program=PROGRAM, version=misc.version)


# the record id at the top of a record's JSON text, or None
def _recordId(text):
    try:
        rid = json.loads(text).get("id")
    except (ValueError, AttributeError):
        return None

    return rid if isinstance(rid, str) and cf.RECORD_ID.fullmatch(rid) else None


# read path as message cls, raising err (with the path) if it is missing or
# breaks its message
def _read(path, cls, err):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise err(_("%s is missing.") % path) from None
    except OSError as e:
        raise err("%s: %s" % (path, e)) from None

    try:
        return mc.from_json(cls, text)
    except mc.ContractError as e:
        raise err("%s: %s" % (path, e)) from None
