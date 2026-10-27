import tests.u as u  # first: trelby.util cannot be the first trelby module loaded
import trelby.trelbyctrl as trelbyctrl

# MyCtrl.importFile: a .fountain is read like Open, through fountain.load
# (readFountain), and the tab stays untitled (fountain-native/io/5)


class FakeSp:
    def __init__(self):
        self.changed = None

    def markChanged(self, changed=True):
        self.changed = changed


class FakeCtrl:
    def __init__(self, sp):
        self.loaded = sp
        self.sp = None
        self.read = []
        self.emptied = False

    def readFountain(self, fileName):
        self.read.append(fileName)
        return self.loaded

    # MyCtrl.createEmptySp: an empty script, no file name
    def createEmptySp(self):
        self.emptied = True
        self.sp = FakeSp()

    def refreshCache(self):
        pass


def testFountainImportReadsLikeOpen():
    sp = FakeSp()
    ctrl = FakeCtrl(sp)

    trelbyctrl.MyCtrl.importFile(ctrl, "/scripts/A.FOUNTAIN")

    assert ctrl.read == ["/scripts/A.FOUNTAIN"]
    assert ctrl.emptied
    assert ctrl.sp is sp
    assert sp.changed is True


def testUnreadableFountainChangesNothing():
    ctrl = FakeCtrl(None)

    trelbyctrl.MyCtrl.importFile(ctrl, "a.fountain")

    assert not ctrl.emptied
    assert ctrl.sp is None
