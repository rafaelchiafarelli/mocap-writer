# the acts of a script (story-structure/acts/2). an act is a marker only:
# each Act break element starts one, and an act's size is the number of
# scenes in it. no wx.

import trelby.screenplay as screenplay


class Act:
    def __init__(self, name, line, scenes):
        # the act break's text, "Act n" when it is empty, or None for the
        # scenes before the first act break
        self.name = name

        # first line of the act (the act break's line, 0 for the part
        # before the first act break)
        self.line = line

        # number of scenes in the act
        self.scenes = scenes

    def __eq__(self, other):
        return (self.name, self.line, self.scenes) == (
            other.name,
            other.line,
            other.scenes,
        )

    def __repr__(self):
        return "Act(%r, %d, %d)" % (self.name, self.line, self.scenes)


# return the acts of sp in order, [] if it has no act break. scenes before
# the first act break are an unnamed first part, listed only if there are
# any.
def actsOf(sp):
    ls = sp.lines
    before = Act(None, 0, 0)
    acts = []
    cur = before

    for i in range(len(ls)):
        if not sp.isFirstLineOfElem(i):
            continue

        lt = ls[i].lt

        if lt == screenplay.ACTBREAK:
            name = ls[i].text.strip() or _("Act %d") % (len(acts) + 1)
            cur = Act(name, i, 0)
            acts.append(cur)

        elif lt == screenplay.SCENE:
            cur.scenes += 1

    if acts and before.scenes:
        acts.insert(0, before)

    return acts


# return the index in acts of the act holding the given line, or None if
# there is none (no acts, or the line is before the first act break and no
# scene is).
def actAt(acts, line):
    found = None

    for i, act in enumerate(acts):
        if act.line <= line:
            found = i
        else:
            break

    return found
