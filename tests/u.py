# ut:ignore
import os

import trelby.config as config
import trelby.fountain as fountain
import trelby.misc as misc
import trelby.screenplay as screenplay
import trelby.util as util
from trelby.line import Line

initDone = False


def init():
    global initDone

    if not initDone:
        misc.init(False)
        util.init(False)

        initDone = True


# return new, empty Screenplay
def new():
    init()

    return screenplay.Screenplay(config.ConfigGlobal())


def fixtureFilePath(filePathRelativeToFixturesDir: str) -> str:
    location = os.path.dirname(__file__) + "/fixtures/"

    return os.path.join(location, filePathRelativeToFixturesDir)


# load a Fountain script from the fixtures directory, with its script
# settings from the .sconf file of the same name if there is one (what
# Script -> Settings -> Load does, without marking the script changed)
def load(filename="test.fountain"):
    init()
    path = fixtureFilePath(filename)

    with open(path, encoding="UTF-8") as f:
        sp = fountain.load(f.read(), config.ConfigGlobal())

    settings = os.path.splitext(path)[0] + ".sconf"
    if os.path.exists(settings):
        with open(settings, encoding="UTF-8") as f:
            sp.cfg.load(f.read())

        sp.cfg.recalc()
        sp.reformatAll()
        sp.paginate()

    return sp


# test.trelby (before 2026-10-25) ended with "Very." as its own dialogue
# element, two empty Action elements and a dialogue "Very", which Fountain
# cannot hold (test.fountain ends with one dialogue "Very.\nVery"). Tests
# that step through those empty lines, or compare with an import of the same
# script, put that ending back.
def withOldEnding(sp):
    assert [str(ln) for ln in sp.lines[-2:]] == ["|:Very.", ".:Very"]

    sp.lines[-2:] = [
        Line(screenplay.LB_LAST, screenplay.DIALOGUE, "Very."),
        Line(screenplay.LB_LAST, screenplay.ACTION, ""),
        Line(screenplay.LB_LAST, screenplay.ACTION, ""),
        Line(screenplay.LB_LAST, screenplay.DIALOGUE, "Very"),
    ]
    sp.paginate()

    return sp


# load script from a Fountain string
def loadString(s: str):
    init()

    return fountain.load(s, config.ConfigGlobal())
