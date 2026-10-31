import wx

import trelby.importfilm as importfilm

TITLES = {"set": "Sets", "character": "Characters", "prop": "Props"}


# the bible review (import-to-film/flow/2): everything the script offers
# to the bible in one dialog, a checklist per map (links to known items
# ticked; new items ticked when tickNew, as at the end of an import,
# decision 1); Create applies all of it at once, Cancel writes nothing.
# without linkScenes (an import into an open film) new items are offered
# without scenes.
class BibleReviewDlg(wx.Dialog):
    def __init__(self, parent, sections, tickNew, linkScenes=True, note=""):
        wx.Dialog.__init__(
            self, parent, -1, _("Bible from the script"),
            size=parent.FromDIP(wx.Size(520, 620)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.sections = sections
        self.lists = {}
        vsizer = wx.BoxSizer(wx.VERTICAL)

        if note:
            vsizer.Add(wx.StaticText(self, -1, note), 0, wx.ALL, 8)

        for sec in sections:
            lines = sec.lines()
            vsizer.Add(wx.StaticText(self, -1, "%s (%d)" % (_(TITLES[sec.map]), len(lines))),
                       0, wx.LEFT | wx.TOP, 8)
            lb = wx.CheckListBox(self, -1, choices=[self.label(k, l, linkScenes) for k, l in lines])

            for i, (k, _l) in enumerate(lines):
                lb.Check(i, k == "link" or tickNew)

            vsizer.Add(lb, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
            self.lists[sec.map] = lb

        self.notProps = wx.CheckBox(self, -1, _("Mark the new props left unticked as not a prop"))
        vsizer.Add(self.notProps, 0, wx.ALL, 8)
        vsizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.ALL | wx.EXPAND, 8)
        self.FindWindowById(wx.ID_OK).SetLabel(_("Create"))
        self.SetSizer(vsizer)

    @staticmethod
    def label(kind, line, linkScenes):
        if kind == "link":
            it, scene = line

            return _("Link scene %s to %s") % (scene, it.name)

        name, scenes = line

        if not linkScenes:
            return _("New: %s") % name

        return _("New: %s (scenes %s)") % (name, ", ".join(scenes))

    # {map: [checked line indexes]}
    def chosen(self):
        return {m: list(lb.GetCheckedItems()) for m, lb in self.lists.items()}


# plan, ask and apply; returns {map: [items made]}, or None if cancelled
# or there was nothing to review
def review(parent, b, sp, tickNew, linkScenes=True, note=""):
    sections = importfilm.plan(b, sp)

    if not any(sec.lines() for sec in sections):
        return {}

    dlg = BibleReviewDlg(parent, sections, tickNew, linkScenes, note)
    made = None

    if dlg.ShowModal() == wx.ID_OK:
        made = importfilm.apply(b, sections, dlg.chosen(), dlg.notProps.GetValue(), linkScenes)

    dlg.Destroy()

    return made
