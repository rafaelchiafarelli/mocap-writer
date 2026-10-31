from unittest import mock

import tests.u as u
import trelby.screenplay as screenplay
import trelby.titles as titles
from trelby.line import Line


# accepting a completion with End is one undo step (bugs/editor/5)
def testEndCompletionIsUndoable():
    sp = u.new()
    sp.lines = [Line(screenplay.LB_LAST, screenplay.CHARACTER, "JO")]
    sp.line, sp.column = 0, 2
    sp.acItems = ["JOHNNY"]
    sp.acSel = 0

    sp.cmd("moveLineEnd")
    assert sp.lines[0].text == "JOHNNY"
    assert sp.column == 6
    assert sp.isModified()

    sp.cmd("undo")
    assert sp.lines[0].text == "JO"


# Titles.sort orders each page's strings by y, then x (bugs/editor/9)
def testTitlesSort():
    t = titles.Titles()
    page = []
    for x, y in ((50.0, 20.0), (10.0, 20.0), (0.0, 5.0)):
        ts = titles.TitleString(["s"], x, y)
        page.append(ts)
    t.pages = [page]

    t.sort()

    assert [(ts.y, ts.x) for ts in t.pages[0]] == [(5.0, 0.0), (20.0, 10.0), (20.0, 50.0)]


# a formatted copy lays text out with the script's settings, not the
# defaults: here the Action indent (bugs/editor/6)
def testFormattedCopyUsesScriptSettings():
    import trelby.trelbyctrl as trelbyctrl

    sp = u.new()
    sp.cfg.getType(screenplay.ACTION).indent = 17
    sp.lines = [Line(screenplay.LB_LAST, screenplay.ACTION, "Some action.")]
    sp.reformatAll()
    sp.paginate()
    sp.setMark(0, 0)
    sp.line, sp.column = 0, len(sp.lines[0].text)

    ctrl = mock.Mock()
    ctrl.sp = sp
    ctrl.gd.cfgGl = sp.cfgGl

    with mock.patch.object(trelbyctrl.wx, "TheClipboard") as clip, mock.patch.object(
        trelbyctrl.wx, "TextDataObject", side_effect=lambda text: text
    ):
        trelbyctrl.MyCtrl.OnCopySystem(ctrl, formatted=True)

    text = clip.AddData.call_args[0][0]
    assert " " * 17 + "Some action." in text.splitlines()


# the screen's CONTINUED (n) number on any page is the PDF's
# (Screenplay.sceneContNrAt, bugs/editor/8)
def testSceneContNrMatchesPdf():
    import trelby.mypager as mypager

    text = "INT. ONE - DAY\n\n" + "Action line that goes on.\n\n" * 150
    text += "EXT. TWO - NIGHT\n\n" + "More action here.\n\n" * 120
    sp = u.loadString(text)
    sp.cfg.sceneContinueds = True
    sp.paginate()
    assert len(sp.pages) > 6

    pager = mypager.Pager(sp.cfg)
    seen = set()
    for pageNr in range(1, len(sp.pages)):
        assert pager.sceneContNr == sp.sceneContNrAt(pageNr), pageNr
        seen.add(pager.sceneContNr)
        sp.generatePMLPage(pager, pageNr, True, True)

    assert max(seen) >= 2


# side by side: scrolling down shows the cursor's page as the last one on
# screen, up as the first (bugs/editor/7)
def testSideBySideScrollDirection():
    import trelby.config as config
    import trelby.viewmode as viewmode

    text = "INT. ONE - DAY\n\n" + "Action line that goes on.\n\n" * 400
    sp = u.loadString(text)
    sp.cfgGl.recenterOnScroll = False
    assert len(sp.pages) > 10

    ctrl = mock.Mock()
    ctrl.sp = sp
    ctrl.pageW = 100
    ctrl.GetClientSize.return_value = (10 + 3 * 110, 500)  # 3 pages
    vm = viewmode.ViewModeSideBySide()

    line = sp.page2lines(8)[0] + 2
    vm.makeLineVisible(ctrl, line, [], config.SCROLL_DOWN)
    assert sp.line2page(sp.getTopLine()) == 6

    vm.makeLineVisible(ctrl, line, [], config.SCROLL_UP)
    assert sp.line2page(sp.getTopLine()) == 8

    vm.makeLineVisible(ctrl, line, [], config.SCROLL_CENTER)
    assert sp.line2page(sp.getTopLine()) == 7

    vm.makeLineVisible(ctrl, sp.page2lines(1)[0], [], config.SCROLL_DOWN)
    assert sp.line2page(sp.getTopLine()) == 1


# a page wider than the widget scrolls sideways and follows the cursor
# (bugs/editor/12)
def testHorizontalScroll():
    import trelby.viewmode as viewmode

    # fits: centered, the scroll ignored
    assert viewmode.contentLeft(1000, 600, 0) == 200
    assert viewmode.contentLeft(1000, 600, 300) == 200

    # wider: moved left by the scroll, kept within the page
    assert viewmode.contentLeft(500, 800, 0) == 0
    assert viewmode.contentLeft(500, 800, 120) == -120
    assert viewmode.contentLeft(500, 800, 999) == -300
    assert viewmode.clampOffset(-5, 500, 800) == 0

    # the cursor past the right edge: scrolled so it is H_MARGIN inside
    m = viewmode.H_MARGIN
    assert viewmode.followOffset(0, 600, 10, 500, 2000) == 600 + 10 - (500 - m)

    # past the left edge
    assert viewmode.followOffset(300, -50, 10, 500, 2000) == 300 - 50 - m

    # in view: unchanged
    assert viewmode.followOffset(100, 200, 10, 500, 2000) == 100

    # never past the page's end
    assert viewmode.followOffset(0, 5000, 10, 500, 2000) == 1500


# side by side, one page wider than the widget moves with the scroll
def testSideBySideScrollsSideways():
    import trelby.viewmode as viewmode

    vm = viewmode.ViewModeSideBySide()
    ctrl = mock.Mock()
    ctrl.pageW = 800

    assert vm.getContentWidth(ctrl) == 800 + 2 * viewmode.SBS_PAGE_GAP
