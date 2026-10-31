import wx

from trelby.actpanel import ActPanel

# temporary until we can find out a way to separate MyCtrl
from trelby.trelbyctrl import MyCtrl


class MyPanel(wx.Panel):

    def __init__(self, parent, id, gd):
        wx.Panel.__init__(
            self,
            parent,
            id,
            # wxMSW/Windows does not seem to support
            # wx.NO_BORDER, which sucks
            style=wx.WANTS_CHARS | wx.NO_BORDER,
        )

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.scrollBar = wx.ScrollBar(self, -1, style=wx.SB_VERTICAL)

        # under the script, shown only while the page is wider than it
        # (bugs/editor/12)
        self.hScrollBar = wx.ScrollBar(self, -1, style=wx.SB_HORIZONTAL)
        self.hScrollBar.Hide()

        # the acts of this script, fixed at the right
        # (story-structure/acts/2). made before MyCtrl, whose constructor
        # already updates it.
        self.actPanel = ActPanel(self, -1, gd)

        self.ctrl = MyCtrl(self, -1, gd)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.ctrl, 1, wx.EXPAND)
        vsizer.Add(self.hScrollBar, 0, wx.EXPAND)

        hsizer.Add(vsizer, 1, wx.EXPAND)
        hsizer.Add(self.scrollBar, 0, wx.EXPAND)
        hsizer.Add(self.actPanel, 0, wx.EXPAND)

        self.scrollBar.Bind(wx.EVT_COMMAND_SCROLL, self.ctrl.OnScroll)

        self.scrollBar.Bind(wx.EVT_SET_FOCUS, self.OnScrollbarFocus)

        self.hScrollBar.Bind(wx.EVT_COMMAND_SCROLL, self.ctrl.OnHScroll)
        self.hScrollBar.Bind(wx.EVT_SET_FOCUS, self.OnScrollbarFocus)

        self.SetSizer(hsizer)

    # we never want the scrollbar to get the keyboard focus, pass it on to
    # the main widget
    def OnScrollbarFocus(self, event):
        self.ctrl.SetFocus()
