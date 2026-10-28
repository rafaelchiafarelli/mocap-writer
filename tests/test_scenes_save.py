import tests.u as u
import trelby.fountain as fountain
import trelby.scenenumbers as sn
import trelby.screenplay as scr
from trelby.line import Line

# numbers given on save, OMITTED, Renumber all (fountain-native/scenes/3)

SCRIPT = """INT. ONE #1#

One.

INT. TWO #2#

Two.

INT. THREE #3#

Three.
"""


def scenes(sp):
    return [(sp.lines[line].text, n) for line, n in sn.scenesOf(sp)]


def nums(sp):
    return [n for _line, n in sn.scenesOf(sp)]


def save(sp):
    assert sn.prepareSave(sp) == []

    return fountain.generate(sp).text


def appendScene(sp, heading, action="Text."):
    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.lines.append(Line(scr.LB_LAST, scr.SCENE, heading))
    sp.lines.append(Line(scr.LB_LAST, scr.ACTION, action))


def insertSceneBefore(sp, i, heading):
    line = sn.scenesOf(sp)[i][0]
    sp.lines[line:line] = [
        Line(scr.LB_LAST, scr.SCENE, heading),
        Line(scr.LB_LAST, scr.ACTION, "New."),
    ]


def deleteScene(sp, i):
    sc = sn.scenesOf(sp)
    line = sc[i][0]
    end = sc[i + 1][0] if i + 1 < len(sc) else len(sp.lines)
    del sp.lines[line:end]


def testNewScriptGetsOneToN():
    sp = u.loadString("INT. A\n\nx\n\nINT. B\n\ny\n")

    text = save(sp)

    assert "INT. A #1#\n" in text
    assert "INT. B #2#\n" in text
    assert sp.sceneNumbersIssued == {"1", "2"}


def testNothingToDoMakesNoUndo():
    sp = u.loadString(SCRIPT)

    assert save(sp) == SCRIPT
    assert sp.lastUndo is None


def testAppendedSceneGetsNextNumber():
    sp = u.loadString(SCRIPT)
    appendScene(sp, "INT. FOUR")
    save(sp)

    assert nums(sp) == ["1", "2", "3", "4"]


def testInsertedSceneGetsLetter():
    sp = u.loadString(SCRIPT)
    insertSceneBefore(sp, 1, "INT. ONE AND A HALF")
    save(sp)

    assert scenes(sp)[1] == ("INT. ONE AND A HALF", "1.A")
    assert nums(sp) == ["1", "1.A", "2", "3"]


def testDeletedSceneLeavesOmitted():
    sp = u.loadString(SCRIPT)
    deleteScene(sp, 1)
    text = save(sp)

    assert scenes(sp) == [("INT. ONE", "1"), ("OMITTED", "2"), ("INT. THREE", "3")]
    assert ".OMITTED #2#\n" in text

    # OMITTED reads back as a scene with its number, and stays
    sp2 = u.loadString(text)

    assert nums(sp2) == ["1", "2", "3"]
    assert save(sp2) == text


def testDeletedLastSceneOmittedAtEnd():
    sp = u.loadString(SCRIPT)
    deleteScene(sp, 2)
    save(sp)

    assert scenes(sp)[-1] == ("OMITTED", "3")


def testHeadingTurnedIntoActionIsOmitted():
    sp = u.loadString(SCRIPT)
    line = sn.scenesOf(sp)[1][0]
    sp.line, sp.column = line, 0
    sp.convertTypeTo(scr.ACTION, True)
    save(sp)

    assert scenes(sp) == [("INT. ONE", "1"), ("OMITTED", "2"), ("INT. THREE", "3")]

    # the number left the action line
    assert [ln.text for ln in sp.lines if ln.num] == ["INT. ONE", "OMITTED", "INT. THREE"]


def testSceneMadeAndRemovedBetweenSavesLeavesNothing():
    sp = u.loadString(SCRIPT)
    appendScene(sp, "INT. FOUR")
    del sp.lines[-2:]

    assert save(sp) == SCRIPT


def testMoveIsOmittedAndNewNumber():
    sp = u.loadString(SCRIPT)
    sc = sn.scenesOf(sp)

    # cut scene 1 and paste it at the end
    sp.line, sp.column = sc[0][0], 0
    sp.cmd("setMark")
    sp.line = sc[1][0] - 1
    sp.column = len(sp.lines[sp.line].text)
    cd = sp.getSelectedAsCD(True)

    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.cmd("splitElement")
    sp.paste(cd.lines)
    save(sp)

    assert scenes(sp) == [
        ("OMITTED", "1"),
        ("INT. TWO", "2"),
        ("INT. THREE", "3"),
        ("INT. ONE", "4"),
    ]


def testCopyGetsNewNumber():
    sp = u.loadString(SCRIPT)
    sc = sn.scenesOf(sp)
    sp.line, sp.column = sc[0][0], 0
    sp.cmd("setMark")
    sp.line = sc[1][0] - 1
    sp.column = len(sp.lines[sp.line].text)
    cd = sp.getSelectedAsCD(False)
    sp.clearMark()

    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.cmd("splitElement")
    sp.paste(cd.lines)
    save(sp)

    assert scenes(sp)[0] == ("INT. ONE", "1")
    assert scenes(sp)[-1] == ("INT. ONE", "4")


def testNoRoomStopsTheSave():
    sp = u.loadString("INT. A #1#\n\nx\n\nINT. B #1.A#\n\ny\n")
    insertSceneBefore(sp, 1, "INT. NEW")
    before = [str(ln) for ln in sp.lines]

    msgs = sn.prepareSave(sp)

    assert len(msgs) == 1
    assert "INT. NEW" in msgs[0]
    assert [str(ln) for ln in sp.lines] == before
    assert sp.lastUndo is None


def testBeforeTheFirstSceneIsNoRoom():
    sp = u.loadString(SCRIPT)
    insertSceneBefore(sp, 0, "INT. COLD OPEN")

    assert sn.prepareSave(sp) != []


def testDuplicateStopsTheSave():
    sp = u.loadString("INT. A #1#\n\nx\n\nINT. B #1#\n\ny\n")
    msgs = sn.prepareSave(sp)

    assert msgs == ["Scene 1 is numbered more than once: INT. B"]


def testOneUndoStepBringsBackTheStateBeforeTheSave():
    sp = u.loadString(SCRIPT)
    deleteScene(sp, 1)
    insertSceneBefore(sp, 1, "INT. NEW")
    before = [str(ln) for ln in sp.lines]
    issued = set(sp.sceneNumbersIssued)
    save(sp)

    # OMITTED goes right before the next higher number, so the new scene
    # in the deleted one's place is an insert after 1
    assert scenes(sp) == [
        ("INT. ONE", "1"),
        ("INT. NEW", "1.A"),
        ("OMITTED", "2"),
        ("INT. THREE", "3"),
    ]

    after = [str(ln) for ln in sp.lines]
    sp.cmd("undo")

    assert [str(ln) for ln in sp.lines] == before
    assert sp.sceneNumbersIssued == issued

    sp.cmd("redo")

    assert [str(ln) for ln in sp.lines] == after
    assert "1.A" in sp.sceneNumbersIssued


def testRenumberAll():
    sp = u.loadString(SCRIPT)
    deleteScene(sp, 1)
    insertSceneBefore(sp, 1, "INT. NEW")
    save(sp)
    before = [str(ln) for ln in sp.lines]

    sn.renumberAll(sp)

    assert scenes(sp) == [("INT. ONE", "1"), ("INT. NEW", "2"), ("INT. THREE", "3")]
    assert sp.sceneNumbersIssued == {"1", "2", "3"}

    # nothing comes back as OMITTED on the next save
    text = save(sp)

    assert "OMITTED" not in text
    assert sp.lastUndo.prev is not None

    sp.cmd("undo")

    assert [str(ln) for ln in sp.lines] == before
    assert sp.sceneNumbersIssued == {"1", "1.A", "2", "3"}


def testRenumberAllWithCursorInOmitted():
    sp = u.loadString(SCRIPT)
    deleteScene(sp, 1)
    save(sp)
    sp.line = sn.scenesOf(sp)[1][0]

    sn.renumberAll(sp)
    sp._validate()

    assert 0 <= sp.line < len(sp.lines)
