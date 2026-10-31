from unittest import mock

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


# other formats are picked by their extension, in any case: SCRIPT.FDX is
# Final Draft, a name merely ending in "fdx" is plain text
# (bugs/import-export/3)
def testImportPicksFormatByExtension():
    cases = [
        ("SCRIPT.FDX", "importFDX"),
        ("a.Celtx", "importCeltx"),
        ("a.astx", "importAstx"),
        ("a.FADEIN", "importFadein"),
        ("a.Pdf", "importPdf"),
        ("notesfdx", "importTextFile"),
        ("a.txt", "importTextFile"),
    ]
    for fileName, func in cases:
        ctrl = FakeCtrl(None)
        ctrl.gd = mock.Mock()
        with mock.patch.object(trelbyctrl.myimport, func, return_value=None) as f:
            trelbyctrl.MyCtrl.importFile(ctrl, fileName)
        assert f.called, fileName
