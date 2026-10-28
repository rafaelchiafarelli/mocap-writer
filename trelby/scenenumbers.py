# permanent scene numbers (fountain-native/scenes). a number never changes
# once given; a scene inserted later gets a letter, and levels alternate
# number and letter with a dot between them: 12, 12.A, 12.A.1, 12.A.1.A.
# the number is the scene's identity. no wx.

import math
import re
from collections import namedtuple

import trelby.screenplay as screenplay
import trelby.undo as undo
from trelby.line import Line

NUMBER_RE = re.compile(r"^[1-9][0-9]*$")
LETTER_RE = re.compile(r"^[A-Z]$")

# a problem with the numbers of a script: kind is one of the PROBLEM_*
# values, index the scene's index in the list given to check(), number its
# number ("" when it has none)
Problem = namedtuple("Problem", "kind index number")

(PROBLEM_DUPLICATE, PROBLEM_ORDER, PROBLEM_FOREIGN, PROBLEM_MISSING) = (
    "duplicate",
    "order",
    "foreign",
    "missing",
)


# "12.A.1" -> (12, "A", 1); None if s is not in the writer's form (another
# tool's number, such as "1A" or "I-1-A", or nothing)
def parse(s):
    if not s:
        return None

    ret = []

    for i, part in enumerate(s.split(".")):
        if i % 2 == 0:
            if not NUMBER_RE.match(part):
                return None

            ret.append(int(part))
        else:
            if not LETTER_RE.match(part):
                return None

            ret.append(part)

    return tuple(ret)


# (12, "A", 1) -> "12.A.1"
def fmt(t):
    return ".".join(str(x) for x in t)


# sort key of a number in the writer's form: a scene's children come after
# it and before its next sibling (12 < 12.A < 12.A.1 < 12.B < 13)
def key(s):
    return parse(s)


def _nextSibling(t):
    last = t[-1]

    if isinstance(last, int):
        return t[:-1] + (last + 1,)

    if last == "Z":
        return None

    return t[:-1] + (chr(ord(last) + 1),)


def _firstChild(t):
    if isinstance(t[-1], int):
        return t + ("A",)

    return t + (1,)


# whether q is below p (p's child, grandchild...)
def _isBelow(q, p):
    return len(q) > len(p) and q[: len(p)] == p


# the number for a new scene after p (the number before it, parsed) and
# before q (the next existing number, parsed, or None at the end); highest
# is the highest number in the script. None if no number fits.
def _between(p, q, highest):
    if q is None:
        return (highest[0] + 1,)

    sibling = _nextSibling(p)

    # a sibling only when q is outside p's parent, so a whole number never
    # gets the next whole number in the middle of the script
    if sibling and p[:-1] and not _isBelow(q, p[:-1]):
        return sibling

    if _isBelow(q, p):
        return None

    return _firstChild(p)


# give every scene without a number one by the rule. nums is a list of
# numbers (str) or None, in script order. returns (new, noRoom): new is
# the same list with the numbers given, noRoom the indexes left None.
def assign(nums):
    new = list(nums)
    noRoom = []
    parsed = [parse(n) if n else None for n in nums]

    if all(n is None for n in nums):
        return ([str(i + 1) for i in range(len(nums))], [])

    highest = max((p for p in parsed if p), default=(0,))

    # p: the number before the current scene, parsed; False when it is in
    # another tool's form, None when there is none
    p = None

    for i, n in enumerate(nums):
        if n is not None:
            p = parsed[i] or False

            continue

        q = None
        foreignQ = False

        for j in range(i + 1, len(nums)):
            if nums[j] is not None:
                q = parsed[j]
                foreignQ = q is None

                break

        if foreignQ or p is False:
            noRoom.append(i)

            continue

        if p is None:
            # before the first numbered scene: 1, when that scene is not 1
            # (fountain-native/scenes/6)
            t = (1,) if (1,) < q else None
        else:
            t = _between(p, q, highest)

        if t is None:
            noRoom.append(i)

            continue

        new[i] = fmt(t)
        p = t

        if t > highest:
            highest = t

    return (new, noRoom)


# problems with the numbers of a script (nums as for assign): duplicates
# (every one after the first), numbers out of order, numbers in another
# tool's form, scenes with no number
def check(nums):
    ret = []
    seen = set()
    last = None

    for i, n in enumerate(nums):
        if not n:
            ret.append(Problem(PROBLEM_MISSING, i, ""))

            continue

        if n in seen:
            ret.append(Problem(PROBLEM_DUPLICATE, i, n))

            continue

        seen.add(n)
        t = parse(n)

        if t is None:
            ret.append(Problem(PROBLEM_FOREIGN, i, n))

            continue

        if last is not None and t <= last:
            ret.append(Problem(PROBLEM_ORDER, i, n))

        last = t

    return ret


# the scene headings of sp, in order: [(line, num)], line the heading's
# first line, num its number ("" if none). an empty heading is not a scene
# (Fountain does not write it).
def scenesOf(sp):
    ls = sp.lines
    ret = []
    i = 0

    while i < len(ls):
        last = sp.getElemLastIndexFromLine(i)

        if ls[i].lt == screenplay.SCENE and any(
            ls[j].text.strip() for j in range(i, last + 1)
        ):
            ret.append((i, ls[i].num))

        i = last + 1

    return ret


# the problems with sp's scene numbers as text for the user, "" if there
# are none. nothing is fixed (fountain-native/scenes/2).
def report(sp):
    scenes = scenesOf(sp)
    problems = check([n or None for _line, n in scenes])

    if not problems:
        return ""

    def heading(p):
        return sp.lines[scenes[p.index][0]].text

    out = []
    missing = [p for p in problems if p.kind == PROBLEM_MISSING]

    for p in problems:
        if p.kind == PROBLEM_DUPLICATE:
            out.append(
                _("Scene {} is numbered more than once: {}").format(
                    p.number, heading(p)
                )
            )
        elif p.kind == PROBLEM_ORDER:
            out.append(
                _("Scene {} is out of order: {}").format(p.number, heading(p))
            )
        elif p.kind == PROBLEM_FOREIGN:
            out.append(
                _(
                    "Scene number {} is not in the writer's form (12, 12.A, "
                    "12.A.1); no scene can be inserted right after it: {}"
                ).format(p.number, heading(p))
            )

    if missing:
        out.append(
            _(
                "{} of {} scenes have no number yet; they get one now, by "
                "their place in the script."
            ).format(len(missing), len(scenes))
        )

    return "\n".join(out)


# the text of an OMITTED heading, the place of a deleted scene
OMITTED = "OMITTED"


def _sortKey(n):
    return parse(n) or (math.inf, n)


# give every finished scene heading without a number its number
# (fountain-native/scenes/6): a heading is finished when it has text and
# the cursor is not in it. same plan as prepareSave; never the heading
# holding the cursor, except in a script with no number at all yet (opened
# or imported without them), which is numbered 1..n at once so the
# heading under the cursor does not end up after its successor. only
# Line.num changes, so no undo step is made and no undo step's line ranges
# move. returns True if a number was given.
def numberFinished(sp):
    p = _plan(sp)
    first, last = sp.getElemIndexesFromLine(sp.line)
    changed = False

    if not any(n for _k, n in p.merged):
        first, last = -1, -1

    for (k, old), n in zip(p.merged, p.new):
        if k is None or old or not n:
            continue

        line = p.scenes[k][0]

        if first <= line <= last:
            continue

        sp.lines[line].num = n
        changed = True

    if changed:
        sp.markChanged()

    return changed


# what a save would do to sp's scene numbers, changing nothing: a Plan of
# scenes (scenesOf), stray (lines holding a number but no longer a heading),
# omitted ([(scene index it goes before, number)]), merged (the scenes and
# OMITTED headings to come in order: (scene index or None, number or
# None)), new and noRoom (assign() over merged)
Plan = namedtuple("Plan", "scenes stray present omitted merged new noRoom")


def _plan(sp):
    ls = sp.lines
    scenes = scenesOf(sp)
    sceneLines = {line for line, _n in scenes}
    stray = [i for i, ln in enumerate(ls) if ln.num and i not in sceneLines]
    present = {n for _line, n in scenes if n}

    # each vanished number goes before the first numbered scene after it,
    # else at the end
    def place(n):
        t = parse(n)

        if t is not None:
            for k, (_line, num) in enumerate(scenes):
                pt = parse(num)

                if pt is not None and pt > t:
                    return k

        return len(scenes)

    omitted = sorted(
        ((place(n), n) for n in sp.sceneNumbersIssued if n not in present),
        key=lambda x: (x[0], _sortKey(x[1])),
    )

    merged = []
    o = 0

    for k in range(len(scenes) + 1):
        while o < len(omitted) and omitted[o][0] == k:
            merged.append((None, omitted[o][1]))
            o += 1

        if k < len(scenes):
            merged.append((k, scenes[k][1] or None))

    new, noRoom = assign([n for _k, n in merged])

    return Plan(scenes, stray, present, omitted, merged, new, noRoom)


# the number shown for each scene heading: {line: label}, the number, or
# for a scene not numbered yet the one a save would give it in parentheses
# ("(12.A)"), "?" when no number fits (fountain-native/scenes/4)
def labels(sp):
    p = _plan(sp)
    ret = {}

    for (k, old), n in zip(p.merged, p.new):
        if k is not None:
            ret[p.scenes[k][0]] = old or ("(%s)" % n if n else "?")

    return ret


# the label of the scene holding line (labels as from labels()), "" if
# the line is before the first scene
def labelAt(labs, line):
    best = -1

    for k in labs:
        if best < k <= line:
            best = k

    return labs.get(best, "")


# get sp's scene numbers ready for a save (fountain-native/scenes/3): a
# number given before (sp.sceneNumbersIssued) and no longer on a heading
# comes back as an OMITTED heading at its place by number order; a number
# left on a line that is no longer a heading is removed; every scene
# without a number gets one by assign(). all of it is one undo step, made
# only when something changes. returns [] when the script can be saved, or
# the reasons it cannot (duplicates, no room) as text, changing nothing.
def prepareSave(sp):
    ls = sp.lines
    scenes, stray, present, omitted, merged, new, noRoom = _plan(sp)
    nums = [n for _k, n in merged]

    def heading(i):
        k = merged[i][0]

        return OMITTED if k is None else ls[scenes[k][0]].text

    msgs = [
        _("Scene {} is numbered more than once: {}").format(p.number, heading(p.index))
        for p in check(nums)
        if p.kind == PROBLEM_DUPLICATE
    ]

    msgs += [
        _(
            "No number fits the new scene {}: it is right before the first "
            "numbered scene, right after a scene and before its first insert, "
            "or next to a number in another form."
        ).format(heading(i))
        for i in noRoom
    ]

    if msgs:
        return msgs

    given = [
        (scenes[k][0], n) for (k, old), n in zip(merged, new) if k is not None and not old
    ]

    if not (stray or omitted or given):
        sp.sceneNumbersIssued = present

        return []

    u = undo.SceneNumbers(sp)

    for i in stray:
        ls[i].num = ""

    for line, n in given:
        ls[line].num = n

    for k, n in reversed(omitted):
        at = scenes[k][0] if k < len(scenes) else len(ls)
        ls.insert(at, Line(screenplay.LB_LAST, screenplay.SCENE, OMITTED, n))

        if at <= sp.line:
            sp.line += 1

    sp.sceneNumbersIssued = {n for _line, n in scenesOf(sp) if n}
    sp.paginate()
    sp.markChanged()

    u.setAfter(sp)
    sp.addUndo(u)

    return []


# Script -> Renumber all scenes: every scene, in order, gets 1, 2, 3...;
# the OMITTED headings go (their numbers mean nothing after a renumber);
# one undo step. the numbers given so far become the new ones, so the old
# ones do not come back as OMITTED.
def renumberAll(sp):
    u = undo.SceneNumbers(sp)
    ls = sp.lines
    keep = []
    i = 0

    while i < len(ls):
        last = sp.getElemLastIndexFromLine(i)
        text = " ".join(ls[j].text for j in range(i, last + 1)).strip()

        if ls[i].lt == screenplay.SCENE and text.upper() == OMITTED:
            if i <= sp.line:
                sp.line -= min(last, sp.line) - i + 1
        else:
            keep.extend(ls[i : last + 1])

        i = last + 1

    if not keep:
        keep.append(Line(screenplay.LB_LAST, screenplay.SCENE))

    sp.lines = keep

    for ln in keep:
        ln.num = ""

    for k, (line, _n) in enumerate(scenesOf(sp)):
        keep[line].num = str(k + 1)

    sp.sceneNumbersIssued = {ln.num for ln in keep if ln.num}
    sp.validatePos()
    sp.clearMark()
    sp.paginate()
    sp.markChanged()

    u.setAfter(sp)
    sp.addUndo(u)


# the warning shown when a scene number is clicked: "do not show this again
# for the next 5 clicks" (fountain-native/scenes/4)
class ClickWarning:
    SNOOZE = 5

    def __init__(self):
        # clicks left on which the warning is not shown
        self.skip = 0

    # a click on a number: whether to show the warning
    def click(self):
        if self.skip > 0:
            self.skip -= 1

            return False

        return True

    # the user ticked "do not show this again for the next 5 clicks"
    def snooze(self):
        self.skip = self.SNOOZE


# one for the whole program, while it runs
clickWarning = ClickWarning()
