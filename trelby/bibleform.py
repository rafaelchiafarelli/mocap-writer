import wx

import trelby.bibleedit as bibleedit

# the form of one bible item (film-bible/maps/1-4), under the bible tree.
# one form for every map, generated from the catalog (bibleedit.groups): a
# header per group, and per field its control and a state button. a value
# is saved when its control loses the focus or Enter is pressed, as
# creator-approved; the state button shows where a value stands (script
# stated, approved, a proposal, TBD) and approves a proposal. a per-scene
# group has its own scene choice. files are added with a button or dropped
# on the field.

STATE_LABELS = {
    None: "",
    "script-stated": "script",
    "creator-approved": "ok",
    "proposal": "proposal",
    "tbd": "TBD",
}


# width of the label column in pixels at 96 dpi
LABEL_WIDTH = 110


class FileDrop(wx.FileDropTarget):
    def __init__(self, fn):
        wx.FileDropTarget.__init__(self)
        self.fn = fn

    def OnDropFiles(self, x, y, filenames):
        wx.CallAfter(self.fn, list(filenames))

        return True


class BibleForm(wx.ScrolledWindow):
    def __init__(self, parent, id, panel):
        wx.ScrolledWindow.__init__(self, parent, id, style=wx.VSCROLL)
        self.SetScrollRate(0, 10)

        # the BiblePanel
        self.panel = panel

        self.item = None

        # field name -> (control, state button, group)
        self.rows = {}

        # group key -> selected scene number
        self.scenes = {}

        # group key -> scene wx.ComboBox
        self.sceneCtrls = {}

        # True while the controls are rebuilt: a control destroyed then
        # loses the focus, and must not save into the item shown next
        self.building = False

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))

    @property
    def bible(self):
        return self.panel.bible

    def setItem(self, item):
        if item is not self.item:
            self.commitFocused()
            self.scenes = {}

        self.item = item
        self.build()

    # the open script's Screenplay, for the scene choices
    def script(self):
        try:
            return self.panel.frame.panel.ctrl.sp
        except AttributeError:
            return None

    # save the field being typed in, if any
    def commitFocused(self):
        focus = wx.Window.FindFocus()

        for name, (ctrl, _b, _g) in self.rows.items():
            if ctrl is focus:
                self.OnCommit(name)

    def build(self):
        self.building = True

        try:
            self.doBuild()
        finally:
            self.building = False

    def doBuild(self):
        self.DestroyChildren()
        self.rows = {}
        self.sceneCtrls = {}
        sizer = self.GetSizer()
        sizer.Clear()

        if self.item is None:
            return

        it = self.item
        title = wx.StaticText(self, -1, it.name)
        title.SetFont(title.GetFont().Bold().Larger())
        sizer.Add(title, 0, wx.LEFT | wx.TOP | wx.RIGHT, 6)
        sizer.Add(wx.StaticText(self, -1, "%s   %s" % (it.id, it.folder)), 0, wx.LEFT, 6)

        grid = self.newGrid(sizer)
        self.aliases = wx.TextCtrl(self, -1, "; ".join(it.msg.aliases), style=wx.TE_PROCESS_ENTER)
        self.aliases.SetToolTip(_("Other names, separated by ;"))
        self.aliases.Bind(wx.EVT_KILL_FOCUS, self.OnAliases)
        self.aliases.Bind(wx.EVT_TEXT_ENTER, self.OnAliases)
        grid.Add(self.label(_("Aliases")), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.aliases, 1, wx.EXPAND)
        grid.Add((1, 1))

        scenes = sorted(self.bible.scenes(it))
        grid.Add(self.label(_("Scenes")), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(wx.StaticText(self, -1, ", ".join(scenes) or _("none yet")))
        grid.Add((1, 1))

        if it.map == "wardrobe":
            # who wears it in which scenes (film-bible/links/3)
            box = wx.BoxSizer(wx.HORIZONTAL)
            self.worn = wx.TextCtrl(
                self, -1, bibleedit.wornText(self.bible, it), style=wx.TE_READONLY
            )
            self.worn.SetMinSize(wx.Size(self.FromDIP(40), -1))
            btn = wx.Button(self, -1, "...", style=wx.BU_EXACTFIT)
            btn.Bind(wx.EVT_BUTTON, self.OnWorn)
            box.Add(self.worn, 1, wx.EXPAND)
            box.Add(btn, 0, wx.LEFT, 3)
            grid.Add(self.label(_("Worn by")), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(box, 1, wx.EXPAND)
            grid.Add((1, 1))

        for g in bibleedit.groups(it.map):
            self.addGroup(sizer, g)

        self.FitInside()
        self.Layout()

    def newGrid(self, sizer):
        grid = wx.FlexGridSizer(3, 4, 6)
        grid.AddGrowableCol(1, 1)
        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 6)

        return grid

    def addGroup(self, sizer, g):
        head = wx.StaticText(self, -1, g.label)
        head.SetFont(head.GetFont().Bold())
        sizer.Add(head, 0, wx.LEFT | wx.TOP, 6)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
        grid = self.newGrid(sizer)
        scene = None

        if g.perScene:
            choices = bibleedit.sceneChoices(self.bible, self.item, self.script())
            scene = self.scenes.get(g.key) or (choices[0] if choices else None)
            self.scenes[g.key] = scene
            cb = wx.ComboBox(
                self, -1, scene or "", choices=choices, style=wx.TE_PROCESS_ENTER
            )
            cb.SetMinSize(wx.Size(self.FromDIP(60), -1))
            cb.SetToolTip(_("The scene these values are for (its number)"))
            cb.Bind(wx.EVT_COMBOBOX, lambda e, k=g.key: self.OnScene(k))
            cb.Bind(wx.EVT_TEXT_ENTER, lambda e, k=g.key: self.OnScene(k))
            self.sceneCtrls[g.key] = cb
            grid.Add(self.label(_("Scene")), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(cb, 1, wx.EXPAND)
            grid.Add((1, 1))

            if scene is None:
                grid.Add(wx.StaticText(self, -1, ""))
                grid.Add(wx.StaticText(self, -1, _("Type a scene number to fill this in.")))
                grid.Add((1, 1))

                return

        for f in g.fields:
            self.addField(grid, g, f, scene)

    # a field label: the same width in every group, wrapped, so the
    # columns line up and the form never grows wider than the panel
    def label(self, text):
        w = self.FromDIP(LABEL_WIDTH)
        st = wx.StaticText(self, -1, text)
        st.Wrap(w)
        st.SetMinSize(wx.Size(w, -1))

        return st

    def addField(self, grid, g, f, scene):
        label = f.label + (" (%s)" % f.unit if f.unit else "")
        grid.Add(self.label(label), 0, wx.ALIGN_CENTER_VERTICAL)
        value = bibleedit.text(self.bible, self.item, f.name, scene)

        if f.type in ("link", "file"):
            box = wx.BoxSizer(wx.HORIZONTAL)
            ctrl = wx.TextCtrl(self, -1, value, style=wx.TE_READONLY)
            ctrl.SetMinSize(wx.Size(self.FromDIP(40), -1))
            btn = wx.Button(self, -1, _("Add...") if f.type == "file" else "...", style=wx.BU_EXACTFIT)
            box.Add(ctrl, 1, wx.EXPAND)
            box.Add(btn, 0, wx.LEFT, 3)
            grid.Add(box, 1, wx.EXPAND)

            if f.type == "file":
                btn.Bind(wx.EVT_BUTTON, lambda e, n=f.name: self.OnAddFile(n))
                drop = FileDrop(lambda paths, n=f.name: self.addFiles(n, paths))
                ctrl.SetDropTarget(drop)
                ctrl.Bind(wx.EVT_LEFT_DCLICK, lambda e, n=f.name: self.OnFileMenu(n))
            else:
                btn.Bind(wx.EVT_BUTTON, lambda e, n=f.name: self.OnLinks(n))
        elif f.type == "choice":
            ctrl = wx.ComboBox(self, -1, value, choices=list(f.options), style=wx.TE_PROCESS_ENTER)
            ctrl.SetMinSize(wx.Size(self.FromDIP(60), -1))
            ctrl.Bind(wx.EVT_COMBOBOX, lambda e, n=f.name: self.OnCommit(n))
            grid.Add(ctrl, 1, wx.EXPAND)
        else:
            multi = f.name in ("general.description", "general.notes") or f.name.endswith("backstory")
            style = wx.TE_MULTILINE if multi else wx.TE_PROCESS_ENTER
            ctrl = wx.TextCtrl(self, -1, value, style=style)
            ctrl.SetMinSize(wx.Size(self.FromDIP(60), -1))

            if multi:
                ctrl.SetMinSize(wx.Size(self.FromDIP(60), self.FromDIP(54)))

            if f.type == "list":
                ctrl.SetToolTip(_("Several values, separated by ;"))

            grid.Add(ctrl, 1, wx.EXPAND)

        if f.type not in ("link", "file"):
            ctrl.Bind(wx.EVT_KILL_FOCUS, lambda e, n=f.name: (self.OnCommit(n), e.Skip()))

            if ctrl.HasFlag(wx.TE_PROCESS_ENTER):
                ctrl.Bind(wx.EVT_TEXT_ENTER, lambda e, n=f.name: self.OnCommit(n))

        st = bibleedit.stateOf(self.bible, self.item, f.name, scene)
        sbtn = wx.Button(self, -1, STATE_LABELS[st], style=wx.BU_EXACTFIT)
        sbtn.SetMinSize(wx.Size(self.FromDIP(56), -1))
        sbtn.SetToolTip(bibleedit.describe(self.bible, self.item, f.name, scene))
        sbtn.Enable(st is not None)

        if st == "proposal":
            sbtn.SetForegroundColour(wx.Colour(180, 90, 0))
        elif st == "tbd":
            sbtn.SetForegroundColour(wx.Colour(170, 0, 0))

        sbtn.Bind(wx.EVT_BUTTON, lambda e, n=f.name: self.OnStateMenu(n))
        grid.Add(sbtn)
        self.rows[f.name] = (ctrl, sbtn, g)

    def sceneOf(self, name):
        g = self.rows[name][2]

        return self.scenes.get(g.key) if g.perScene else None

    # run fn; what the film refuses is shown and the form shows the item as
    # it is again
    def guard(self, fn, *args):
        try:
            return fn(*args)
        except Exception as e:
            wx.MessageBox(str(e), _("Bible"), wx.OK, self)
            wx.CallAfter(self.build)

            return None

    def refreshRow(self, name):
        ctrl, sbtn, g = self.rows[name]
        scene = self.sceneOf(name)
        st = bibleedit.stateOf(self.bible, self.item, name, scene)
        sbtn.SetLabel(STATE_LABELS[st])
        sbtn.Enable(st is not None)
        sbtn.SetToolTip(bibleedit.describe(self.bible, self.item, name, scene))
        sbtn.SetForegroundColour(wx.NullColour)
        value = bibleedit.text(self.bible, self.item, name, scene)

        if ctrl.GetValue() != value:
            ctrl.ChangeValue(value)

    def OnCommit(self, name):
        if self.building or self.item is None or name not in self.rows:
            return

        ctrl = self.rows[name][0]

        if self.guard(
            bibleedit.commit, self.bible, self.item, name, ctrl.GetValue(), self.sceneOf(name)
        ):
            self.refreshRow(name)

    def OnAliases(self, event):
        event.Skip()

        if self.building or self.item is None:
            return

        new = [a.strip() for a in self.aliases.GetValue().split(";") if a.strip()]

        if new != list(self.item.msg.aliases):
            def save():
                del self.item.msg.aliases[:]
                self.item.msg.aliases.extend(new)
                self.bible.save(self.item, "creator")

            self.guard(save)

    def OnScene(self, key):
        scene = self.sceneCtrls[key].GetValue().strip()

        if scene and scene != self.scenes.get(key):
            self.scenes[key] = scene
            wx.CallAfter(self.build)

    def OnStateMenu(self, name):
        st = bibleedit.stateOf(self.bible, self.item, name, self.sceneOf(name))
        menu = wx.Menu()
        acts = []

        if st == "proposal":
            acts.append((_("Approve"), "creator-approved"))

        for s, label in (
            ("creator-approved", _("Approved by the creator")),
            ("script-stated", _("Stated by the script...")),
            ("proposal", _("A proposal")),
            ("tbd", _("To be decided...")),
        ):
            if s != st:
                acts.append((label, s))

        for label, s in acts:
            mi = menu.Append(-1, label)
            self.Bind(wx.EVT_MENU, lambda e, s=s: self.setState(name, s), id=mi.GetId())

        self.PopupMenu(menu)
        menu.Destroy()

    def setState(self, name, state):
        source = revisit = None

        if state == "script-stated":
            source = self.ask(_("The scene number that states it:"), self.sceneOf(name) or "")

            if source is None:
                return
        elif state == "tbd":
            revisit = self.ask(_("What reopens it (the revisit trigger):"), "")

            if not revisit:
                return
        elif state == "creator-approved":
            source = bibleedit.creatorSource()

        self.guard(
            bibleedit.setState, self.bible, self.item, name, state, self.sceneOf(name),
            source, revisit,
        )
        self.refreshRow(name)

    def ask(self, prompt, value):
        dlg = wx.TextEntryDialog(self, prompt, _("Bible"), value)
        ret = dlg.GetValue().strip() if dlg.ShowModal() == wx.ID_OK else None
        dlg.Destroy()

        return ret

    def OnLinks(self, name):
        choices = bibleedit.linkChoices(self.bible, self.item, name)
        scene = self.sceneOf(name)
        current = [v.text for v in self.bible.values(self.item, name, scene)]

        if not choices:
            wx.MessageBox(_("There is nothing to link to yet."), _("Bible"), wx.OK, self)

            return

        dlg = wx.MultiChoiceDialog(
            self, _("Link to:"), _("Bible"), [n for _i, n in choices]
        )
        dlg.SetSelections([i for i, (rid, _n) in enumerate(choices) if rid in current])

        if dlg.ShowModal() == wx.ID_OK:
            ids = [choices[i][0] for i in dlg.GetSelections()]
            self.guard(bibleedit.setLinks, self.bible, self.item, name, ids, scene)
            self.refreshRow(name)

        dlg.Destroy()

    def OnAddFile(self, name):
        dlg = wx.FileDialog(self, _("Files to add"), style=wx.FD_OPEN | wx.FD_MULTIPLE)

        if dlg.ShowModal() == wx.ID_OK:
            self.addFiles(name, dlg.GetPaths())

        dlg.Destroy()

    def addFiles(self, name, paths):
        if self.item is not None and paths:
            self.guard(bibleedit.addFiles, self.bible, self.item, name, paths, self.sceneOf(name))
            self.refreshRow(name)

    # double click on a file field: remove one of its files
    def OnFileMenu(self, name):
        rels = [v.text for v in self.bible.values(self.item, name, self.sceneOf(name))]

        if not rels:
            return

        dlg = wx.SingleChoiceDialog(self, _("Remove which file?"), _("Bible"), rels)

        if dlg.ShowModal() == wx.ID_OK:
            self.guard(
                bibleedit.removeFile, self.bible, self.item, name,
                rels[dlg.GetSelection()], self.sceneOf(name),
            )
            self.refreshRow(name)

        dlg.Destroy()

    # link the wardrobe item to a character in scenes: pick the character,
    # then tick the scenes it is worn in
    def OnWorn(self, event=None):
        chars = sorted(
            (c for c in self.bible.items.values() if c.map == "character"),
            key=lambda c: c.name.lower(),
        )

        if not chars:
            wx.MessageBox(_("There are no characters in the bible yet."), _("Bible"), wx.OK, self)

            return

        dlg = wx.SingleChoiceDialog(
            self, _("Worn by which character?"), _("Bible"), [c.name for c in chars]
        )
        char = chars[dlg.GetSelection()] if dlg.ShowModal() == wx.ID_OK else None
        dlg.Destroy()

        if char is None:
            return

        scenes = bibleedit.sceneChoices(self.bible, self.item, self.script())
        worn = bibleedit.wornScenes(self.item, char.id)

        for s in worn:
            if s not in scenes:
                scenes.append(s)

        if not scenes:
            wx.MessageBox(_("The script has no numbered scenes yet."), _("Bible"), wx.OK, self)

            return

        dlg = wx.MultiChoiceDialog(
            self, _("Scenes %s wears it in:") % char.name, _("Bible"), scenes
        )
        dlg.SetSelections([i for i, s in enumerate(scenes) if s in worn])

        if dlg.ShowModal() == wx.ID_OK:
            chosen = [scenes[i] for i in dlg.GetSelections()]
            self.guard(bibleedit.setWorn, self.bible, self.item, char, chosen)
            wx.CallAfter(self.build)

        dlg.Destroy()
