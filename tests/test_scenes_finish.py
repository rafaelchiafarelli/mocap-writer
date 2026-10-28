import tests.u as u
import trelby.scenenumbers as sn
import trelby.screenplay as scr
from trelby.line import Line

# a scene gets its number when its heading is finished: it has text and
# the cursor is not in it (fountain-native/scenes/6). the editor calls
# numberFinished before each screen update; here the tests call it.

SCRIPT = """INT. ONE #1#

One.

INT. TWO #2#

Two.
"""


def nums(sp):
    return [n for _line, n in sn.scenesOf(sp)]


def typeHeadingAtEnd(sp, text):
    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.cmd("splitElement")
    sp.convertTypeTo(scr.SCENE, True)
    sp.cmdChars(text)


def testNoNumberWhileTyping():
    sp = u.loadString(SCRIPT)
    typeHeadingAtEnd(sp, "INT. THREE")

    assert not sn.numberFinished(sp)
    assert nums(sp) == ["1", "2", ""]
    assert list(sn.labels(sp).values())[-1] == "(3)"


def testEnterFinishesTheHeading():
    sp = u.loadString(SCRIPT)
    typeHeadingAtEnd(sp, "INT. THREE")
    sp.cmd("splitElement")

    assert sn.numberFinished(sp)
    assert nums(sp) == ["1", "2", "3"]
    assert sp.isModified()


def testMovingAwayFinishesTheHeading():
    sp = u.loadString(SCRIPT)
    line = sn.scenesOf(sp)[1][0]
    sp.lines[line:line] = [
        Line(scr.LB_LAST, scr.SCENE, "INT. NEW"),
        Line(scr.LB_LAST, scr.ACTION, "New."),
    ]
    sp.line, sp.column = line, 0

    sn.numberFinished(sp)

    assert nums(sp) == ["1", "", "2"]

    sp.gotoPos(0, 0)
    sn.numberFinished(sp)

    assert nums(sp) == ["1", "1.A", "2"]


def testEmptyHeadingGetsNoNumber():
    sp = u.loadString(SCRIPT)
    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.cmd("splitElement")
    sp.convertTypeTo(scr.SCENE, True)
    sp.cmd("splitElement")

    assert not sn.numberFinished(sp)
    assert nums(sp) == ["1", "2"]


def testPastedHeadingIsNumberedAtOnce():
    sp = u.loadString(SCRIPT)
    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.cmd("splitElement")
    sp.paste(
        [
            Line(scr.LB_LAST, scr.SCENE, "INT. PASTED"),
            Line(scr.LB_LAST, scr.ACTION, "Pasted."),
        ]
    )
    sn.numberFinished(sp)

    assert nums(sp) == ["1", "2", "3"]


def testUnnumberedScriptIsNumberedAtOnce():
    sp = u.loadString("INT. A\n\nx\n\nINT. B\n\ny\n\nINT. C\n\nz\n")

    # the cursor is in a heading; it is numbered too, so it keeps its place
    sp.line, sp.column = sn.scenesOf(sp)[1][0], 0
    sn.numberFinished(sp)

    assert nums(sp) == ["1", "2", "3"]


def testScriptWithSomeNumbersSkipsTheCursorHeading():
    sp = u.loadString("INT. A\n\nx\n\nINT. B #2#\n\ny\n")
    sp.line, sp.column = 0, 0
    sn.numberFinished(sp)

    assert nums(sp) == ["", "2"]

    sp.gotoPos(len(sp.lines) - 1, 0)
    sn.numberFinished(sp)

    assert nums(sp) == ["1", "2"]


def testNoRoomStaysUnnumbered():
    sp = u.loadString("INT. A #1#\n\nx\n\nINT. B #1.A#\n\ny\n")
    line = sn.scenesOf(sp)[1][0]
    sp.lines[line:line] = [Line(scr.LB_LAST, scr.SCENE, "INT. NEW")]
    sn.numberFinished(sp)

    assert nums(sp) == ["1", "", "1.A"]
    assert list(sn.labels(sp).values()) == ["1", "?", "1.A"]


def testUndoTakesTheNumberAwayAndLeavingGivesItBack():
    sp = u.loadString(SCRIPT)
    typeHeadingAtEnd(sp, "INT. THREE")
    sp.cmd("splitElement")
    sn.numberFinished(sp)

    assert nums(sp) == ["1", "2", "3"]

    sp.cmd("undo")

    # back in the heading, as it was before Enter: no number yet
    assert nums(sp) == ["1", "2", ""]
    assert not sn.numberFinished(sp)

    sp.cmd("redo")
    sn.numberFinished(sp)

    assert nums(sp) == ["1", "2", "3"]
    sp._validate()


def testSaveStillNumbersTheHeadingBeingTyped():
    sp = u.loadString(SCRIPT)
    typeHeadingAtEnd(sp, "INT. THREE")

    assert sn.prepareSave(sp) == []
    assert nums(sp) == ["1", "2", "3"]
