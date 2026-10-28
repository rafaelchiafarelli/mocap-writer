import tests.u as u
import trelby.mypager as mypager
import trelby.pml as pml
import trelby.scenenumbers as sn
import trelby.scenereport as scenereport
import trelby.screenplay as scr
from trelby.line import Line

# scene numbers on screen, in the PDF, in Go to scene and the scene report;
# the click warning's counter (fountain-native/scenes/4)

SCRIPT = """INT. ONE #1#

One.

INT. TWO #2#

Two.
"""


def withNewScene(sp):
    # a scene between 1 and 2, not numbered yet
    line = sn.scenesOf(sp)[1][0]
    sp.lines[line:line] = [
        Line(scr.LB_LAST, scr.SCENE, "INT. NEW"),
        Line(scr.LB_LAST, scr.ACTION, "New."),
    ]
    sp.paginate()

    return sp


def pageTexts(sp, forPDF):
    pager = mypager.Pager(sp.cfg)
    texts = []

    for i in range(1, len(sp.pages)):
        pg = sp.generatePMLPage(pager, i, forPDF, True)
        texts += [op for op in pg.ops if isinstance(op, pml.TextOp)]

    return texts


def testLabels():
    sp = withNewScene(u.loadString(SCRIPT))
    labs = sn.labels(sp)

    assert list(labs.values()) == ["1", "(1.A)", "2"]
    assert sn.labelAt(labs, 0) == "1"
    assert sn.labelAt(labs, sn.scenesOf(sp)[1][0] + 1) == "(1.A)"
    assert sn.labelAt({}, 5) == ""


def testNoRoomLabel():
    sp = u.loadString("INT. A #1#\n\nx\n\nINT. B #1.A#\n\ny\n")
    line = sn.scenesOf(sp)[1][0]
    sp.lines[line:line] = [Line(scr.LB_LAST, scr.SCENE, "INT. NEW")]

    assert list(sn.labels(sp).values()) == ["1", "?", "1.A"]


def testPdfPrintsPermanentNumbers():
    sp = withNewScene(u.loadString(SCRIPT))
    sp.cfg.pdfShowSceneNumbers = True

    texts = [op.text for op in pageTexts(sp, True)]

    # left and right of each heading
    assert texts.count("1") == 2
    assert texts.count("(1.A)") == 2
    assert texts.count("2") == 2


def testPdfWithoutNumbersWhenOff():
    sp = u.loadString(SCRIPT)
    sp.cfg.pdfShowSceneNumbers = False

    assert "1" not in [op.text for op in pageTexts(sp, True)]


def testScreenAlwaysShowsNumbersAndTagsThem():
    sp = u.loadString(SCRIPT)
    sp.cfg.pdfShowSceneNumbers = False
    ops = [op for op in pageTexts(sp, False) if getattr(op, "sceneLine", -1) >= 0]
    heading = sn.scenesOf(sp)[1][0]

    assert sorted(op.text for op in ops) == ["1", "1", "2", "2"]
    assert {op.sceneLine for op in ops if op.text == "2"} == {heading}

    # never part of the heading's text
    assert sp.lines[heading].text == "INT. TWO"


def testTocUsesNumbers():
    sp = u.loadString(SCRIPT)
    sp.cfg.pdfShowSceneNumbers = True
    sp.cfg.pdfIncludeTOC = True
    doc = sp.generatePML(True)
    items = [op.toc.text for pg in doc.pages for op in pg.ops if getattr(op, "toc", None)]

    assert items == ["1 INT. ONE", "2 INT. TWO"]


def testGotoSceneList():
    sp = withNewScene(u.loadString(SCRIPT))

    assert sp.getSceneLocations() == [
        ("1", sn.scenesOf(sp)[0][0]),
        ("2", sn.scenesOf(sp)[2][0]),
    ]


def testSceneReportNumbers():
    sp = withNewScene(u.loadString(SCRIPT))
    report = scenereport.SceneReport(sp)

    assert [si.number for si in report.scenes] == ["1", "(1.A)", "2"]


def testClickWarningCounter():
    w = sn.ClickWarning()

    assert w.click()
    assert w.click()

    w.snooze()

    assert [w.click() for _ in range(6)] == [False] * 5 + [True]
