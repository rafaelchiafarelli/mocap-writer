import wx

import trelby.bible as bible
import trelby.review as review

# column labels (translated when the dialog is made) and widths
COLUMNS = (("Scene", 90), ("Item", 120), ("Field", 140), ("Value", 180), ("Why", 90),
           ("Source", 110))


# the review view (preprod-link/review/1): the proposals, TBDs and values
# needing review in one list, grouped by scene; from the keyboard, A
# approves, R rejects and E (or Enter) edits the selected lines, one or a
# batch (Ctrl+A selects all). nothing is written before a key or button.
class ReviewDlg(wx.Dialog):
    def __init__(self, frame, bible_, changes=None):
        wx.Dialog.__init__(
            self, frame, -1, _("Review proposals"), size=frame.FromDIP(wx.Size(820, 520)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.frame = frame
        self.bible = bible_
        self.changes = changes

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(
            wx.StaticText(self, -1, _("A approve   R reject   E or Enter edit   Ctrl+A all")),
            0, wx.ALL, 8,
        )
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)

        for i, (label, width) in enumerate(COLUMNS):
            self.list.InsertColumn(i, _(label), width=self.FromDIP(width))

        self.list.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda e: self.OnEdit())
        vsizer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        for label, fn in ((_("&Approve"), self.OnApprove), (_("&Reject"), self.OnReject),
                          (_("&Edit..."), self.OnEdit)):
            btn = wx.Button(self, -1, label)
            btn.Bind(wx.EVT_BUTTON, lambda e, fn=fn: fn())
            hsizer.Add(btn, 0, wx.RIGHT, 6)

        closeBtn = wx.Button(self, wx.ID_CLOSE)
        closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        hsizer.Add(closeBtn)
        vsizer.Add(hsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8)
        self.SetSizer(vsizer)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Destroy())

        # the needs-review lines approved in this session leave the list
        self.done = set()
        self.fill()

    def fill(self):
        self.list.DeleteAllItems()
        self.entries = [
            e for e in review.queue(self.bible, self.changes)
            if (e.item.id, e.value.SerializeToString()) not in self.done
        ]

        for e in self.entries:
            scene = e.scene or (_("all: %s") % ", ".join(review.appliesTo(self.bible, e)))
            f = bible.cb.fields(e.item.map).get(e.value.field)
            row = (scene, e.item.name, f.label if f else e.value.field,
                   review.valueText(e.value), _(e.why), e.value.source)
            i = self.list.InsertItem(self.list.GetItemCount(), row[0])

            for c, text in enumerate(row[1:], 1):
                self.list.SetItem(i, c, text)

        if self.entries:
            self.list.Select(0)
            self.list.Focus(0)

    def selected(self):
        out = []
        i = self.list.GetFirstSelected()

        while i != -1:
            out.append(self.entries[i])
            i = self.list.GetNextSelected(i)

        return out

    def OnKey(self, event):
        k = event.GetKeyCode()

        if event.ControlDown() and k == ord("A"):
            for i in range(self.list.GetItemCount()):
                self.list.Select(i)
        elif k == ord("A"):
            self.OnApprove()
        elif k == ord("R"):
            self.OnReject()
        elif k == ord("E"):
            self.OnEdit()
        else:
            event.Skip()

    def guard(self, fn, *args):
        try:
            fn(*args)
        except Exception as e:
            wx.MessageBox(str(e), _("Review proposals"), wx.OK, self)

        self.frame.biblePanel.changed()
        self.fill()

    def OnApprove(self):
        es = self.selected()

        for e in es:
            if e.why == review.REVIEW:
                self.done.add((e.item.id, e.value.SerializeToString()))

        self.guard(review.approve, self.bible, es)

    def OnReject(self):
        es = self.selected()

        if es and wx.MessageBox(
            _("Remove %d values?") % len(es), _("Review proposals"), wx.YES_NO, self
        ) == wx.YES:
            self.guard(review.reject, self.bible, es)

    def OnEdit(self):
        es = self.selected()

        if len(es) != 1:
            return

        dlg = wx.TextEntryDialog(
            self, _("%s, new value:") % es[0].item.name, _("Review proposals"),
            review.valueText(es[0].value),
        )

        if dlg.ShowModal() == wx.ID_OK:
            self.guard(review.edit, self.bible, es[0], dlg.GetValue())

        dlg.Destroy()
