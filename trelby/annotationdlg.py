import datetime

import mocap_contracts as mc
from mocap_contracts import annotation as ca

import wx

import trelby.annotations as annotations
import trelby.bible as bible
import trelby.bibleedit as bibleedit
import trelby.util as util

# the dialogs of the script's annotations (fountain-native/notes/1): one
# annotation's kind, text and fields (generated from the annotation
# catalog), and the list of the annotations at the cursor or unattached.


class AnnotationDlg(wx.Dialog):
    # a is the mc.Annotation to edit, or None for a new one; where says
    # what it is anchored to; bib is the film's bible.Bible (link choices)
    def __init__(self, parent, a, where, bib):
        wx.Dialog.__init__(
            self,
            parent,
            -1,
            _("Annotation"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.a = a
        self.bib = bib

        # field name -> (control, Field)
        self.controls = {}

        # link field name -> [ids]
        self.links = {}

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(self, -1, where), 0, wx.BOTTOM, 6)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(self, -1, _("Kind")), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.kind = wx.Choice(
            self, -1, choices=[_(annotations.KIND_LABELS[k]) for k in annotations.KINDS]
        )
        self.kind.SetSelection(
            annotations.KINDS.index(ca.kind_word(a.kind)) if a else 0
        )
        self.kind.Enable(a is None)
        hsizer.Add(self.kind, 1)
        vsizer.Add(hsizer, 0, wx.EXPAND)

        vsizer.Add(wx.StaticText(self, -1, _("Text")), 0, wx.TOP, 6)
        self.text = wx.TextCtrl(
            self, -1, a.text if a and a.HasField("text") else "", style=wx.TE_MULTILINE
        )
        self.text.SetMinSize(wx.Size(self.FromDIP(420), self.FromDIP(60)))
        vsizer.Add(self.text, 0, wx.EXPAND)

        self.fields = wx.ScrolledWindow(self, -1, style=wx.VSCROLL)
        self.fields.SetScrollRate(0, 10)
        self.fields.SetMinSize(wx.Size(self.FromDIP(420), self.FromDIP(280)))
        self.fields.SetSizer(wx.BoxSizer(wx.VERTICAL))
        vsizer.Add(self.fields, 1, wx.EXPAND | wx.TOP, 6)

        vsizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.TOP, 10)

        util.finishWindow(self, vsizer)

        self.Bind(wx.EVT_CHOICE, self.OnKind, id=self.kind.GetId())
        self.buildFields()

    def kindWord(self):
        return annotations.KINDS[self.kind.GetSelection()]

    def OnKind(self, event):
        self.buildFields()

    def current(self, name):
        if self.a is None:
            return []

        return [v for v in self.a.values if v.field == name]

    def buildFields(self):
        self.fields.DestroyChildren()
        sizer = self.fields.GetSizer()
        sizer.Clear()
        self.controls = {}
        self.links = {}
        group = None
        grid = None

        for f in ca.fields(self.kindWord()).values():
            if f.group != group:
                group = f.group
                head = wx.StaticText(self.fields, -1, f.group_label)
                head.SetFont(head.GetFont().Bold())
                sizer.Add(head, 0, wx.TOP, 6)
                grid = wx.FlexGridSizer(2, 4, 6)
                grid.AddGrowableCol(1, 1)
                sizer.Add(grid, 0, wx.EXPAND)

            label = f.label + (" (%s)" % f.unit if f.unit else "")
            st = wx.StaticText(self.fields, -1, label)
            st.Wrap(self.FromDIP(150))
            grid.Add(st, 0, wx.ALIGN_CENTER_VERTICAL)
            vs = self.current(f.name)

            if f.type == "number":
                ctrl = wx.TextCtrl(self.fields, -1, vs[0].number if vs else "")
            elif f.type == "choice":
                ctrl = wx.ComboBox(self.fields, -1, vs[0].text if vs else "", choices=list(f.options))
            elif f.type == "link":
                self.links[f.name] = [v.text for v in vs]
                box = wx.BoxSizer(wx.HORIZONTAL)
                ctrl = wx.TextCtrl(self.fields, -1, self.linkNames(f.name), style=wx.TE_READONLY)
                btn = wx.Button(self.fields, -1, "...", style=wx.BU_EXACTFIT)
                btn.Bind(wx.EVT_BUTTON, lambda e, f=f, c=ctrl: self.OnLinks(f, c))
                box.Add(ctrl, 1, wx.EXPAND)
                box.Add(btn, 0, wx.LEFT, 3)
                grid.Add(box, 1, wx.EXPAND)
                self.controls[f.name] = (ctrl, f)

                continue
            elif f.type == "file":
                ctrl = wx.StaticText(
                    self.fields, -1, "; ".join(v.text for v in vs) or _("(files: not here yet)")
                )
            else:
                ctrl = wx.TextCtrl(self.fields, -1, "; ".join(v.text for v in vs))

            grid.Add(ctrl, 1, wx.EXPAND)
            self.controls[f.name] = (ctrl, f)

        self.fields.FitInside()
        self.Layout()

    def linkNames(self, name):
        names = []

        for rid in self.links[name]:
            it = self.bib.get(rid) if self.bib else None
            names.append(it.name if it else rid)

        return "; ".join(names)

    def OnLinks(self, f, ctrl):
        items = sorted(
            (it for it in (self.bib.items.values() if self.bib else []) if it.map == f.link_kind),
            key=lambda it: it.name.lower(),
        )

        if not items:
            wx.MessageBox(_("There is nothing in the bible to link to yet."), _("Annotation"), wx.OK, self)

            return

        dlg = wx.MultiChoiceDialog(self, _("Link to:"), _("Annotation"), [it.name for it in items])
        dlg.SetSelections([i for i, it in enumerate(items) if it.id in self.links[f.name]])

        if dlg.ShowModal() == wx.ID_OK:
            self.links[f.name] = [items[i].id for i in dlg.GetSelections()]
            ctrl.SetValue(self.linkNames(f.name))

        dlg.Destroy()

    # the values typed, as [mc.BibleValue]; the ones unchanged keep their
    # state, source and author; raises ValueError for a bad number
    def values(self):
        source = _("creator %s") % datetime.date.today().isoformat()
        out = []

        for name, (ctrl, f) in self.controls.items():
            old = self.current(name)

            if f.type == "file":
                out.extend(old)

                continue

            if f.type == "link":
                new = list(self.links[name])
            else:
                new = bibleedit.parse(f, ctrl.GetValue())

            oldVals = [(v.number, v.unit) if f.type == "number" else v.text for v in old]

            if new == oldVals:
                out.extend(old)

                continue

            for value in new:
                v = mc.BibleValue(
                    field=name,
                    state=bible.state("creator-approved"),
                    source=source,
                    department=f.department,
                    by="creator",
                )

                if f.type == "number":
                    v.number, v.unit = value
                else:
                    v.text = value

                out.append(v)

        return out


# the annotations of a place, to edit, delete or (for unattached ones)
# re-attach at the cursor
class AnnotationListDlg(wx.Dialog):
    def __init__(self, parent, title, items, canAttach):
        wx.Dialog.__init__(
            self, parent, -1, title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        # [(id, text)]
        self.items = items

        # (action, id) chosen: "edit", "delete", "attach"
        self.chosen = None

        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListBox(
            self, -1, size=wx.Size(self.FromDIP(460), self.FromDIP(220)),
            choices=[t.replace("\n", " | ") for _i, t in items],
        )

        if items:
            self.list.SetSelection(0)

        vsizer.Add(self.list, 1, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        for label, action in (
            (_("Edit..."), "edit"),
            (_("Delete"), "delete"),
        ) + (((_("Attach at the cursor"), "attach"),) if canAttach else ()):
            b = wx.Button(self, -1, label)
            b.Bind(wx.EVT_BUTTON, lambda e, a=action: self.choose(a))
            hsizer.Add(b, 0, wx.RIGHT, 6)

        hsizer.Add((1, 1), 1)
        hsizer.Add(wx.Button(self, wx.ID_CANCEL, _("Close")))
        vsizer.Add(hsizer, 0, wx.EXPAND | wx.TOP, 10)
        util.finishWindow(self, vsizer)
        self.list.Bind(wx.EVT_LISTBOX_DCLICK, lambda e: self.choose("edit"))

    def choose(self, action):
        i = self.list.GetSelection()

        if i != wx.NOT_FOUND:
            self.chosen = (action, self.items[i][0])
            self.EndModal(wx.ID_OK)
