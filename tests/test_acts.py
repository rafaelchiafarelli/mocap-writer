import tests.u as u
import trelby.acts as acts
import trelby.mypager as mypager
import trelby.pml as pml
import trelby.screenplay as screenplay
import trelby.translations as translations
from trelby.line import Line

_ = translations.trelby_translations_load()

# acts (story-structure/acts): the act break is a marker only, never
# printed (acts/1); acts.actsOf / actAt give the acts and their sizes in
# scenes for the act panel (acts/2; the panel itself needs a display).

SCRIPT = """# ACT ONE

INT. ROOM - DAY

Someone waits.

# ACT TWO

EXT. STREET - NIGHT

Someone runs.
"""


def pdfTexts(sp):
    doc = sp.generatePML(True)

    return [
        op.text for page in doc.pages for op in page.ops if isinstance(op, pml.TextOp)
    ]


def testActBreakNotInPdf():
    sp = u.loadString(SCRIPT)
    texts = pdfTexts(sp)

    assert "ACT ONE" not in texts
    assert "ACT TWO" not in texts
    assert "INT. ROOM - DAY" in texts
    assert "Someone runs." in texts


def testTextMovesUpIntoTheMarkersPlace():
    sp = u.loadString(SCRIPT)
    page = sp.generatePML(True).pages[0]
    ys = {op.text: op.y for op in page.ops if isinstance(op, pml.TextOp)}

    # the scene heading takes the first line, where ACT ONE was
    assert ys["INT. ROOM - DAY"] == sp.cfg.marginTop


def testPaginationUnchanged():
    sp = u.load()
    before = list(sp.pages)

    # an act break at the start of every scene
    i = 0
    while i < len(sp.lines):
        if sp.lines[i].lt == screenplay.SCENE and sp.isFirstLineOfElem(i):
            sp.lines.insert(i, Line(screenplay.LB_LAST, screenplay.ACTBREAK, "ACT"))
            i += 1
        i += 1

    sp.paginate()
    paged = list(sp.pages)
    doc = sp.generatePML(True)

    # every page of the pagination is in the PDF, none dropped or added
    assert len(paged) > len(before)
    assert len(doc.pages) == len(paged) - 1 + len(sp.titles.pages)


def testScreenStillShowsTheMarker():
    sp = u.loadString(SCRIPT)
    pager = mypager.Pager(sp.cfg)
    pg = sp.generatePMLPage(pager, 1, False, True)
    texts = [op.text for op in pg.ops if isinstance(op, pml.TextOp)]

    assert "ACT ONE" in texts


def actsOf(s):
    return acts.actsOf(u.loadString(s))


def testNoActBreakNoActs():
    assert actsOf("INT. ROOM - DAY\n\nSomeone waits.\n") == []


def testActsAndTheirScenes():
    sp = u.loadString(SCRIPT + "\nINT. CAR - NIGHT\n\nSomeone drives.\n")
    found = acts.actsOf(sp)

    assert [(a.name, a.scenes) for a in found] == [("ACT ONE", 1), ("ACT TWO", 2)]
    assert sp.lines[found[1].line].text == "ACT TWO"


def testScenesBeforeTheFirstAct():
    found = actsOf("INT. ROOM - DAY\n\nSomeone waits.\n\n" + SCRIPT)

    assert [(a.name, a.scenes) for a in found] == [
        (None, 1),
        ("ACT ONE", 1),
        ("ACT TWO", 1),
    ]
    assert found[0].line == 0


def testNothingBeforeTheFirstActIsNotListed():
    found = actsOf("Someone waits.\n\n" + SCRIPT)

    assert [a.name for a in found] == ["ACT ONE", "ACT TWO"]


def testEmptyNameAndEmptyAct():
    sp = u.loadString(SCRIPT)
    sp.lines[acts.actsOf(sp)[0].line].text = ""

    assert acts.actsOf(sp)[0].name == "Act 1"

    found = actsOf("# ACT ONE\n\n# ACT TWO\n\nINT. ROOM - DAY\n\nSomeone.\n")

    assert [(a.name, a.scenes) for a in found] == [("ACT ONE", 0), ("ACT TWO", 1)]


def testActAt():
    sp = u.loadString("Someone waits.\n\n" + SCRIPT)
    found = acts.actsOf(sp)
    one, two = found[0].line, found[1].line

    assert acts.actAt(found, 0) is None
    assert acts.actAt(found, one) == 0
    assert acts.actAt(found, two - 1) == 0
    assert acts.actAt(found, two) == 1
    assert acts.actAt(found, len(sp.lines) - 1) == 1
    assert acts.actAt([], 5) is None
