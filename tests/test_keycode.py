import wx

import tests.u as u  # first: trelby.util cannot be the first trelby module loaded
import trelby.util as util

# util.eventKeyCode: the key code MyCtrl.OnKeyChar looks commands up by.
# arrows and other non-character keys have no Unicode value; they must
# fall back to their wx.WXK_ code (bugs/editor/13).


class FakeCharEvent:
    def __init__(self, unicodeKey, keyCode):
        self.unicodeKey = unicodeKey
        self.keyCode = keyCode

    def GetUnicodeKey(self):
        return self.unicodeKey

    def GetKeyCode(self):
        return self.keyCode


def testArrowsUseTheirKeyCode():
    for code in (
        wx.WXK_UP,
        wx.WXK_DOWN,
        wx.WXK_LEFT,
        wx.WXK_RIGHT,
        wx.WXK_HOME,
        wx.WXK_END,
        wx.WXK_PAGEUP,
        wx.WXK_PAGEDOWN,
        wx.WXK_F8,
    ):
        assert util.eventKeyCode(FakeCharEvent(wx.WXK_NONE, code)) == code


def testCharactersUseUnicode():
    # an accented letter keeps its Unicode value (the upstream fix for #89)
    assert util.eventKeyCode(FakeCharEvent(ord("ç"), wx.WXK_NONE)) == ord("ç")
    assert util.eventKeyCode(FakeCharEvent(ord("a"), ord("A"))) == ord("a")


def testInsertsReadTheirCharacter():
    # Character map, Name database and non-breaking space insert through a
    # util.MyKeyEvent, which eventKeyCode must be able to read (bugs/editor/1)
    assert util.eventKeyCode(util.MyKeyEvent(160)) == 160
    assert util.eventKeyCode(util.MyKeyEvent(ord("ç"))) == ord("ç")
