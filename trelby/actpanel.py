import wx

import trelby.acts as acts
import trelby.util as util

# the act panel (story-structure/acts/2): right of the editor, one row per
# act with a bar as long as its scene count against the largest act. it
# uses its own pixel fonts, so the zoom never changes it, and it does not
# scroll with the script.


class ActPanel(wx.Window):
    # width in pixels at 96 dpi
    WIDTH = 200

    def __init__(self, parent, id, gd):
        wx.Window.__init__(self, parent, id, style=wx.NO_BORDER)

        self.gd = gd

        # what is drawn: the acts and the index of the cursor's act
        self.acts = []
        self.current = None

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetMinSize((self.FromDIP(self.WIDTH), -1))

        self.font = util.createPixelFont(
            self.FromDIP(13), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL
        )
        self.boldFont = util.createPixelFont(
            self.FromDIP(13), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD
        )

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)

    # read the acts of sp and the act of its cursor line; repaint only if
    # either changed.
    def update(self, sp):
        newActs = acts.actsOf(sp)
        current = acts.actAt(newActs, sp.line)

        if (newActs != self.acts) or (current != self.current):
            self.acts = newActs
            self.current = current
            self.Refresh(False)

    # the keyboard focus stays with the script, as for the scroll bar
    def OnFocus(self, event):
        self.GetParent().ctrl.SetFocus()

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDCFactory(self)
        w, h = self.GetClientSize()

        self.draw(dc, w, h)

    # draw the panel on dc, w x h pixels
    def draw(self, dc, w, h):
        cfgGui = self.gd.cfgGui
        pad = self.FromDIP(8)

        dc.SetBrush(cfgGui.workspaceBrush)
        dc.SetPen(cfgGui.workspacePen)
        dc.DrawRectangle(0, 0, w, h)

        dc.SetPen(cfgGui.pageBorderPen)
        dc.DrawLine(0, 0, 0, h)

        dc.SetTextForeground(cfgGui.textColor)
        dc.SetFont(self.boldFont)
        dc.DrawText(_("Acts"), pad, pad)

        textH = dc.GetTextExtent("Ay")[1]
        y = pad + textH + pad

        if not self.acts:
            dc.SetFont(self.font)
            for s in (_("No acts yet."), _("Add an Act break"), _("to start one.")):
                dc.DrawText(s, pad, y)
                y += textH

            return

        barH = self.FromDIP(8)
        rowH = textH + self.FromDIP(4) + barH + pad
        barW = w - 2 * pad
        most = max(act.scenes for act in self.acts) or 1

        for i, act in enumerate(self.acts):
            isCurrent = i == self.current

            if isCurrent:
                dc.SetBrush(cfgGui.selectedBrush)
                dc.SetPen(cfgGui.selectedPen)
                dc.DrawRectangle(0, y - pad // 2, w, rowH)

            name = act.name if act.name is not None else _("Before the first act")

            if act.scenes == 1:
                count = _("1 scene")
            else:
                count = _("%d scenes") % act.scenes

            dc.SetFont(self.boldFont if isCurrent else self.font)
            countW = dc.GetTextExtent(count)[0]
            dc.DrawText(count, w - pad - countW, y)

            dc.SetClippingRegion(pad, y, max(0, barW - countW - pad), textH)
            dc.DrawText(name, pad, y)
            dc.DestroyClippingRegion()

            by = y + textH + self.FromDIP(4)
            dc.SetBrush(cfgGui.textBgBrush)
            dc.SetPen(cfgGui.pageBorderPen)
            dc.DrawRectangle(pad, by, barW, barH)

            if act.scenes:
                dc.SetBrush(cfgGui.cursorBrush)
                dc.SetPen(cfgGui.cursorPen)
                dc.DrawRectangle(pad, by, max(2, barW * act.scenes // most), barH)

            y += rowH
