import wx

import trelby.biblelinks as biblelinks
import trelby.sync as sync


# the change panel of Sync to spec (preprod-link/sync/2): the run's changes
# grouped by scene; a double click (or Enter) on a line goes to its scene;
# Accept makes the run the last accepted sync. nothing in the bible changes
# from here. modeless, so the creator can read the script beside it.
class SyncDlg(wx.Dialog):
    def __init__(self, frame, film, bible, run):
        wx.Dialog.__init__(
            self, frame, -1, _("Sync to spec"), size=frame.FromDIP(wx.Size(560, 520)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.frame = frame
        self.film = film
        self.bible = bible
        self.run = run

        vsizer = wx.BoxSizer(wx.VERTICAL)
        n = len(run.changes.changes)
        first = not run.changes.HasField("from_hash")
        head = (
            _("First sync: every scene is new.") if first
            else _("%d changes since the last accepted sync.") % n if n
            else _("Nothing changed since the last accepted sync.")
        )
        vsizer.Add(wx.StaticText(self, -1, head), 0, wx.ALL, 8)

        self.tree = wx.TreeCtrl(
            self, -1, style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT
        )
        self.fill()
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnGoto)
        vsizer.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.acceptBtn = wx.Button(self, -1, _("Accept"))
        self.acceptBtn.SetToolTip(_("Make this the last accepted sync"))
        self.acceptBtn.Bind(wx.EVT_BUTTON, self.OnAccept)
        closeBtn = wx.Button(self, wx.ID_CLOSE)
        closeBtn.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        hsizer.Add(self.acceptBtn, 0, wx.RIGHT, 6)
        hsizer.Add(closeBtn)
        vsizer.Add(hsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8)

        self.SetSizer(vsizer)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Destroy())

    def name(self, rid):
        it = self.bible.get(rid) if self.bible else None

        return it.name if it else rid

    # one branch per scene, one line per change, then the bible values
    # that need review there (sync/3); each line's data is the scene number
    def fill(self):
        root = self.tree.AddRoot("")
        heads = {e.scene: e for e in self.run.index.scenes}
        self.sceneNodes = {}
        review = {}

        for a in sync.affected(self.bible, self.run.changes):
            review.setdefault(a.scene, []).append(a)

        for scene, changes in sync.byScene(self.run.changes):
            e = heads.get(scene)
            label = _("Scene %s") % scene + (
                " — " + " ".join(p for p in (e.int_ext, e.location) if p) if e else ""
            )
            node = self.tree.AppendItem(root, label, data=scene)
            self.sceneNodes[scene] = node

            for c in changes:
                self.tree.AppendItem(node, sync.changeText(c, self.name), data=scene)

            for a in review.get(scene, []):
                line = self.tree.AppendItem(node, sync.affectedText(a), data=scene)
                self.tree.SetItemBold(line)

            self.tree.Expand(node)

    # go to the scene of the line
    def OnGoto(self, event):
        scene = self.tree.GetItemData(event.GetItem())
        ctrl = self.frame.panel.ctrl

        for num, first, _last in biblelinks.scenesWithLines(ctrl.sp):
            if num == scene:
                ctrl.sp.line = first
                ctrl.sp.column = 0
                ctrl.makeLineVisible(first)
                ctrl.updateScreen()
                ctrl.SetFocus()

                return

    def OnAccept(self, event=None):
        try:
            sync.accept(self.film, self.run)
        except Exception as e:
            wx.MessageBox(str(e), _("Sync to spec"), wx.OK, self)

            return

        self.acceptBtn.Disable()
        self.acceptBtn.SetLabel(_("Accepted"))
