# permanent scene numbers (fountain-native/scenes). a number never changes
# once given; a scene inserted later gets a letter, and levels alternate
# number and letter with a dot between them: 12, 12.A, 12.A.1, 12.A.1.A.
# the number is the scene's identity. no wx.

import re
from collections import namedtuple

import trelby.screenplay as screenplay

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

        if not p or foreignQ:
            noRoom.append(i)

            continue

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
                "{} of {} scenes have no number yet; they get one when the "
                "script is saved."
            ).format(len(missing), len(scenes))
        )

    return "\n".join(out)
