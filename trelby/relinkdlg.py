import wx

import trelby.relink as relink
import trelby.util as util

# the warning for a film's missing files (file-format/layout/3): one list of
# everything the open could not find or read, shown over the film, which is
# already open behind it; a row with nothing to search for is a notice
# (bugs/editor/21). a missing file can be searched for or skipped; a
# skipped one stays missing and is asked for again on the next open. a found
# one gives a pattern that is tried on the others, and what it finds is
# shown for the creator to accept, never applied silently.


class RelinkDlg(wx.Dialog):
    def __init__(self, parent, root, problems):
        title, intro = relink.warningText(problems)

        wx.Dialog.__init__(
            self,
            parent,
            -1,
            title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.root = root
        self.problems = problems

        # state per row: "missing", "skipped", "found", or None when the
        # problem can't be searched for (an invalid file)
        self.state = [("missing" if p.ref else None) for p in problems]

        vsizer = wx.BoxSizer(wx.VERTICAL)

        vsizer.Add(wx.StaticText(self, -1, intro), 0, wx.BOTTOM, 10)

        self.list = wx.ListCtrl(
            self, -1, size=wx.Size(640, 200), style=wx.LC_REPORT | wx.LC_SINGLE_SEL
        )
        self.list.InsertColumn(0, _("What"), width=160)
        self.list.InsertColumn(1, _("Expected at"), width=220)
        self.list.InsertColumn(2, _("Status"), width=260)

        for i, p in enumerate(problems):
            self.list.InsertItem(i, p.what)
            self.list.SetItem(i, 1, p.where)
            self.list.SetItem(i, 2, _("missing") if p.ref else _("nothing to search for"))

        vsizer.Add(self.list, 1, wx.EXPAND)

        # the selected row's reason in full
        self.detail = wx.StaticText(self, -1, "")
        vsizer.Add(self.detail, 0, wx.EXPAND | wx.TOP, 10)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.searchBtn = wx.Button(self, -1, _("Search..."))
        self.skipBtn = wx.Button(self, -1, _("Skip"))
        closeBtn = wx.Button(self, wx.ID_CLOSE, _("Close"))
        hsizer.Add(self.searchBtn)
        hsizer.Add(self.skipBtn, 0, wx.LEFT, 10)
        hsizer.Add((1, 1), 1)
        hsizer.Add(closeBtn)
        vsizer.Add(hsizer, 0, wx.EXPAND | wx.TOP, 10)

        # only notices: nothing to search for or skip
        if not any(p.ref for p in problems):
            self.searchBtn.Hide()
            self.skipBtn.Hide()

        util.finishWindow(self, vsizer)

        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=self.searchBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnSkip, id=self.skipBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=closeBtn.GetId())
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, id=self.list.GetId())

        first = self.nextOpen(0)
        self.select(first if first != -1 else (0 if problems else -1))

    # index of the first row from i on that still can be searched, or -1
    def nextOpen(self, i):
        for j in list(range(i, len(self.problems))) + list(range(0, i)):
            if self.state[j] == "missing":
                return j

        return -1

    def select(self, i):
        if i != -1:
            self.list.Select(i)
            self.list.Focus(i)

        self.updateButtons()

    def selected(self):
        return self.list.GetFirstSelected()

    def updateButtons(self):
        i = self.selected()
        ok = i != -1 and self.state[i] == "missing"
        self.searchBtn.Enable(bool(ok))
        self.skipBtn.Enable(bool(ok))

        if i == -1:
            text = ""
        elif self.problems[i].ref:
            text = _("Expected at %s.") % self.problems[i].where
        else:
            text = self.problems[i].why

        self.detail.SetLabel(text)
        self.detail.Wrap(640)
        self.Layout()

    def setState(self, i, state, text):
        self.state[i] = state
        self.list.SetItem(i, 2, text)

    def OnSelect(self, event):
        self.updateButtons()

    def OnSkip(self, event=None):
        i = self.selected()

        if i != -1:
            self.setState(i, "skipped", _("skipped"))
            self.select(self.nextOpen(i))

    # ask where the file of row i is: a path, or None
    def askPath(self, i):
        ref = self.problems[i].ref
        msg = _("Where is %s (%s)?") % (ref.what, ref.rel)

        if ref.kind == "folder":
            dlg = wx.DirDialog(self, msg, str(self.root))
        else:
            dlg = wx.FileDialog(self, msg, str(self.root), style=wx.FD_OPEN)

        path = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
        dlg.Destroy()

        return path

    def OnSearch(self, event=None):
        i = self.selected()

        if i == -1:
            return

        ref = self.problems[i].ref
        path = self.askPath(i)

        if path is None:
            return

        rel, why = relink.check(self.root, ref, path)

        if rel is None:
            wx.MessageBox(
                _("%s was not linked.") % path + "\n\n" + why,
                _("Missing files"),
                wx.OK,
                self,
            )

            return

        if not self.apply(i, rel):
            return

        # the same move may explain the others
        others = [
            j
            for j, p in enumerate(self.problems)
            if self.state[j] in ("missing", "skipped")
        ]
        found = relink.suggest(
            self.root,
            relink.pattern(ref.rel, rel),
            [self.problems[j].ref for j in others],
        )

        if found:
            choices = ["%s: %s -> %s" % (r.what, r.rel, n) for r, n in found]
            dlg = wx.MultiChoiceDialog(
                self,
                _("The same move finds these too. Link the ones you accept:"),
                _("Missing files"),
                choices,
            )
            dlg.SetSelections(list(range(len(choices))))

            if dlg.ShowModal() == wx.ID_OK:
                byRef = {id(self.problems[j].ref): j for j in others}

                for k in dlg.GetSelections():
                    r, n = found[k]
                    self.apply(byRef[id(r)], n)

            dlg.Destroy()

        self.select(self.nextOpen(i))

    # save rel for row i where its reference lives; False if that failed
    def apply(self, i, rel):
        try:
            self.problems[i].ref.apply(rel)
        except Exception as e:
            wx.MessageBox(str(e), _("Error"), wx.OK, self)

            return False

        self.setState(i, "found", _("found at %s") % rel)

        return True

    def OnClose(self, event=None):
        self.EndModal(wx.ID_CLOSE)
