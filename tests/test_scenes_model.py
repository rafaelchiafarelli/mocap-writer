import tests.u as u
import trelby.fountain as fountain
import trelby.scenenumbers as scenenumbers
import trelby.screenplay as scr
from trelby.line import Line

# the scene number lives in the model (Line.num) and in the file as
# Fountain's #12# (fountain-native/scenes/2).

SCRIPT = """INT. ROOM - DAY #1#

Someone waits.

EXT. STREET - NIGHT  #1.A#

Someone runs.

.FLASHBACK #2#

Someone remembers.
"""


def nums(sp):
    return [n for _line, n in scenenumbers.scenesOf(sp)]


def save(sp):
    return fountain.generate(sp)


def heading(sp, i):
    return sp.lines[scenenumbers.scenesOf(sp)[i][0]]


def testLoadReadsNumbers():
    sp = u.loadString(SCRIPT)

    assert nums(sp) == ["1", "1.A", "2"]
    assert heading(sp, 1).text == "EXT. STREET - NIGHT"


def testRoundTripByteIdentical():
    sp = u.loadString(SCRIPT)
    res = save(sp)

    assert res.text == SCRIPT
    assert res.lost == []
    assert save(u.loadString(res.text)).text == SCRIPT


def testEditedHeadingKeepsNumberAndSpacing():
    sp = u.loadString(SCRIPT)
    sp.line = scenenumbers.scenesOf(sp)[1][0]
    sp.column = len(sp.lines[sp.line].text)
    sp.cmdChars("X")

    assert heading(sp, 1).num == "1.A"
    assert "EXT. STREET - NIGHTX  #1.A#\n" in save(sp).text


def testChangedNumberIsWritten():
    sp = u.loadString(SCRIPT)
    heading(sp, 0).num = "7"

    text = save(sp).text

    assert text.startswith("INT. ROOM - DAY #7#\n")
    assert nums(u.loadString(text)) == ["7", "1.A", "2"]


def testNumberAddedAndRemoved():
    sp = u.loadString("INT. ROOM - DAY\n\nSomeone waits.\n")
    heading(sp, 0).num = "1"

    assert save(sp).text.startswith("INT. ROOM - DAY #1#\n")

    sp = u.loadString(SCRIPT)
    heading(sp, 0).num = ""

    assert save(sp).text.startswith("INT. ROOM - DAY\n")


def testStrRoundTrip():
    for ln in (
        Line(scr.LB_LAST, scr.SCENE, "INT. X", "12.A"),
        Line(scr.LB_LAST, scr.SCENE, "INT. X"),
        Line(scr.LB_LAST, scr.ACTION, "\x01odd text"),
    ):
        assert Line.fromStr(str(ln)) == ln

    assert Line(text="a", num="1") != Line(text="a")


def testWrapKeepsNumberOnFirstLine():
    sp = u.loadString(SCRIPT)
    first = heading(sp, 0)
    first.text = "INT. A VERY LONG PLACE NAME THAT GOES ON AND ON - " * 3
    sp.rewrapPara(scenenumbers.scenesOf(sp)[0][0])

    line = scenenumbers.scenesOf(sp)[0][0]
    last = sp.getElemLastIndexFromLine(line)

    assert last > line
    assert sp.lines[line].num == "1"
    assert all(not sp.lines[i].num for i in range(line + 1, last + 1))


def testUndoRedoTyping():
    sp = u.loadString(SCRIPT)
    sp.line = scenenumbers.scenesOf(sp)[2][0]
    sp.column = 0
    sp.cmdChars("ABC")
    sp.cmd("undo")

    assert nums(sp) == ["1", "1.A", "2"]

    sp.cmd("redo")

    assert nums(sp) == ["1", "1.A", "2"]


def testJoinHeadingIntoPreviousDropsIt():
    sp = u.loadString(SCRIPT)
    sp.line = scenenumbers.scenesOf(sp)[1][0]
    sp.column = 0
    sp.cmd("deleteBackward")

    assert nums(sp) == ["1", "2"]

    sp.cmd("undo")

    assert nums(sp) == ["1", "1.A", "2"]


def testSplitHeadingKeepsNumberOnFirstPart():
    sp = u.loadString(SCRIPT)
    sp.line = scenenumbers.scenesOf(sp)[0][0]
    sp.column = 4
    sp.cmd("splitElement")

    assert sp.lines[sp.line - 1].num == "1"
    assert not sp.lines[sp.line].num

    sp.cmd("undo")

    assert nums(sp) == ["1", "1.A", "2"]


def testTypeChangeKeepsNumberOnLine():
    sp = u.loadString(SCRIPT)
    line = scenenumbers.scenesOf(sp)[1][0]
    sp.line = line
    sp.column = 0
    sp.convertTypeTo(scr.ACTION, True)

    assert nums(sp) == ["1", "2"]
    assert sp.lines[line].num == "1.A"

    sp.convertTypeTo(scr.SCENE, True)

    assert nums(sp) == ["1", "1.A", "2"]

    sp.cmd("undo")
    sp.cmd("undo")

    assert nums(sp) == ["1", "1.A", "2"]


def selectScene(sp, i):
    line = scenenumbers.scenesOf(sp)[i][0]
    end = (
        scenenumbers.scenesOf(sp)[i + 1][0] - 1
        if i + 1 < len(scenenumbers.scenesOf(sp))
        else len(sp.lines) - 1
    )
    sp.line, sp.column = line, 0
    sp.cmd("setMark")
    sp.line, sp.column = end, len(sp.lines[end].text)


def testCutAndCopyCarryNoNumber():
    sp = u.loadString(SCRIPT)
    selectScene(sp, 1)
    cd = sp.getSelectedAsCD(False)

    assert cd.lines[0].text == "EXT. STREET - NIGHT"
    assert all(not ln.num for ln in cd.lines)

    cd = sp.getSelectedAsCD(True)

    assert all(not ln.num for ln in cd.lines)
    assert nums(sp)[0] == "1"
    assert "1.A" not in nums(sp)

    sp.cmd("undo")

    assert nums(sp) == ["1", "1.A", "2"]


def testPastedSceneHasNoNumber():
    sp = u.loadString(SCRIPT)
    selectScene(sp, 1)
    cd = sp.getSelectedAsCD(False)
    sp.clearMark()
    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.cmd("splitElement")
    sp.paste(cd.lines)

    assert nums(sp) == ["1", "1.A", "2", ""]

    sp.cmd("undo")

    assert nums(sp) == ["1", "1.A", "2"]


def testPasteAtHeadingStartKeepsNumberWithHeading():
    sp = u.loadString(SCRIPT)
    line = scenenumbers.scenesOf(sp)[2][0]
    sp.line, sp.column = line, 0
    sp.paste(
        [
            Line(scr.LB_LAST, scr.ACTION, "Pasted action."),
            Line(scr.LB_LAST, scr.ACTION, "More."),
        ]
    )

    numbered = [sp.lines[i] for i, n in scenenumbers.scenesOf(sp) if n == "2"]

    assert len(numbered) == 1
    assert numbered[0].text == "FLASHBACK"


def testReport():
    assert scenenumbers.report(u.loadString(SCRIPT)) == ""

    msg = scenenumbers.report(
        u.loadString("INT. A #1#\n\nx\n\nINT. B #1#\n\ny\n\nINT. C\n\nz\n")
    )

    assert "Scene 1 is numbered more than once: INT. B" in msg
    assert "1 of 3 scenes have no number yet" in msg

    msg = scenenumbers.report(u.loadString("INT. A #2#\n\nx\n\nINT. B #1A#\n\ny\n"))

    assert "Scene number 1A is not in the writer's form" in msg


def testDeepcopyKeepsNumbers():
    import copy

    sp = u.loadString(SCRIPT)

    assert nums(copy.deepcopy(sp)) == ["1", "1.A", "2"]
