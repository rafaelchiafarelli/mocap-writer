import tests.u as u  # first: trelby.util cannot be the first trelby module loaded
import trelby.trelbyframe as trelbyframe

# MyFrame.saveAll: Save on exit saves every modified tab, not only the
# current one, and calls the exit off if one stays unsaved (bugs/editor/2).


class FakeSp:
    def __init__(self, modified):
        self.modified = modified

    def isModified(self):
        return self.modified


class FakeCtrl:
    def __init__(self, modified, saves=True):
        self.sp = FakeSp(modified)
        self.saves = saves
        self.saved = False

    # like MyCtrl.OnSave: a cancelled Save As leaves the script modified
    def OnSave(self):
        self.saved = True

        if self.saves:
            self.sp.modified = False


class FakePage:
    def __init__(self, ctrl):
        self.ctrl = ctrl


class FakeTabCtrl:
    def __init__(self, ctrls):
        self.pages = [FakePage(c) for c in ctrls]
        self.selected = []

    def getPageCount(self):
        return len(self.pages)

    def getPage(self, i):
        return self.pages[i]

    def selectPage(self, i):
        self.selected.append(i)


class FakeFrame:
    def __init__(self, ctrls):
        self.tabCtrl = FakeTabCtrl(ctrls)


def testSavesEveryModifiedTab():
    ctrls = [FakeCtrl(True), FakeCtrl(False), FakeCtrl(True)]
    frame = FakeFrame(ctrls)

    assert trelbyframe.MyFrame.saveAll(frame)
    assert [c.saved for c in ctrls] == [True, False, True]
    assert frame.tabCtrl.selected == [0, 2]


def testUnsavedTabCallsExitOff():
    ctrls = [FakeCtrl(True, saves=False), FakeCtrl(True)]
    frame = FakeFrame(ctrls)

    assert not trelbyframe.MyFrame.saveAll(frame)
    assert [c.saved for c in ctrls] == [True, False]
