import os

import wx

import trelby.bible as bible
import trelby.bibleedit as bibleedit
import trelby.misc as misc
import trelby.biblelinks as biblelinks
import trelby.bibleform as bibleform

# the bible panel (film-bible/tree/1): left of the script, one tree per map
# (sets, characters, props, wardrobe) like a file explorer, over the open
# film's bible/ folder. selecting an item shows its form under the tree
# (film-bible/maps). shown and hidden with View -> Bible.

MAP_LABELS = {
    "set": "Sets",
    "character": "Characters",
    "prop": "Props",
    "wardrobe": "Wardrobe",
}


class BiblePanel(wx.Panel):
    # width in pixels at 96 dpi
    WIDTH = 360

    def __init__(self, parent, id, frame):
        wx.Panel.__init__(self, parent, id)

        self.frame = frame

        # the open film's bible.Bible, or None
        self.bible = None

        # tree item -> ("map", map) or ("item", id)
        self.nodes = {}

        vsizer = wx.BoxSizer(wx.VERTICAL)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.newBtn = wx.Button(self, -1, _("New"), style=wx.BU_EXACTFIT)
        self.childBtn = wx.Button(self, -1, _("New child"), style=wx.BU_EXACTFIT)
        self.renameBtn = wx.Button(self, -1, _("Rename"), style=wx.BU_EXACTFIT)
        self.deleteBtn = wx.Button(self, -1, _("Delete"), style=wx.BU_EXACTFIT)
        self.scriptBtn = wx.Button(self, -1, _("From script..."), style=wx.BU_EXACTFIT)
        self.scriptBtn.SetToolTip(_("Link the script's scenes to the bible"))

        for b in (self.newBtn, self.childBtn, self.renameBtn, self.deleteBtn, self.scriptBtn):
            hsizer.Add(b, 0, wx.RIGHT, 4)

        vsizer.Add(hsizer, 0, wx.ALL, 4)

        # what the bible links to the cursor's scene (film-bible/links/1)
        self.sceneText = wx.StaticText(self, -1, "")
        vsizer.Add(self.sceneText, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 6)

        # what is in the cursor's scene, by hand (film-bible/links/6)
        self.thisSceneBtn = wx.Button(self, -1, _("This scene..."), style=wx.BU_EXACTFIT)
        self.thisSceneBtn.SetToolTip(_("Tick the sets, characters and props in this scene"))
        self.thisSceneBtn.Bind(wx.EVT_BUTTON, self.OnThisScene)
        self.thisSceneBtn.Enable(False)
        vsizer.Add(self.thisSceneBtn, 0, wx.LEFT | wx.BOTTOM, 4)

        # (scene, text) last shown, so a cursor move repaints nothing
        self.sceneShown = None

        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetMinimumPaneSize(80)

        self.tree = wx.TreeCtrl(
            self.splitter,
            -1,
            style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT
            | wx.TR_SINGLE,
        )

        self.form = self.makeForm(self.splitter)
        self.splitter.SplitHorizontally(self.tree, self.form, 220)

        vsizer.Add(self.splitter, 1, wx.EXPAND)

        self.empty = wx.StaticText(
            self,
            -1,
            _("This tab's script is not a film's.\nFile -> New film or Open film\nto keep a bible."),
        )
        vsizer.Add(self.empty, 0, wx.ALL, 8)

        self.SetSizer(vsizer)

        self.Bind(wx.EVT_BUTTON, self.OnNew, id=self.newBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnNewChild, id=self.childBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnRename, id=self.renameBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=self.deleteBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnScriptMenu, id=self.scriptBtn.GetId())
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
        self.tree.Bind(wx.EVT_TREE_ITEM_MENU, self.OnItemMenu)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)

        self.dragId = None

        self.setBible(None)

    # the selected item's form under the tree (film-bible/maps)
    def makeForm(self, parent):
        return bibleform.BibleForm(parent, -1, self)

    def showItem(self, item):
        self.form.setItem(item)

    def setBible(self, b):
        if b is not self.bible and self.bible is not None:
            # another film's bible (bugs/editor/20): what is being typed is
            # saved into its own film, and nothing stays selected, since
            # ids like set-w-1 repeat from film to film
            self.form.commitFocused()
            self.tree.DeleteAllItems()
            self.nodes = {}

        self.bible = b
        self.splitter.Show(b is not None)
        self.empty.Show(b is None)

        for btn in (self.newBtn, self.childBtn, self.renameBtn, self.deleteBtn, self.scriptBtn):
            btn.Show(b is not None)

        self.refresh()
        self.Layout()

    # rebuild the tree from the bible, keeping the selection and what was
    # expanded
    def refresh(self, selectId=None):
        if selectId is None:
            sel = self.selected()
            selectId = sel[1] if sel else None

        expanded = {
            self.nodes[n] for n in self.nodes if self.tree.IsExpanded(n)
        } if self.nodes else None

        self.tree.DeleteAllItems()
        self.nodes = {}
        root = self.tree.AddRoot("")

        if self.bible is None:
            self.updateButtons()

            return

        toSelect = None

        for map_ in bible.MAPS:
            mapNode = self.tree.AppendItem(root, _(MAP_LABELS[map_]))
            self.nodes[mapNode] = ("map", map_)

            if selectId == map_:
                toSelect = mapNode

            stack = [(mapNode, None)]

            while stack:
                node, parentId = stack.pop()

                for it in self.bible.children(map_, parentId):
                    n = self.tree.AppendItem(node, it.name)
                    self.nodes[n] = ("item", it.id)
                    stack.append((n, it.id))

                    if it.id == selectId:
                        toSelect = n

        # the maps are always open; an item as it was
        for n, key in self.nodes.items():
            if expanded is None or key in expanded or key[0] == "map":
                if self.tree.ItemHasChildren(n):
                    self.tree.Expand(n)

        if toSelect is not None:
            self.tree.EnsureVisible(toSelect)
            self.tree.SelectItem(toSelect)
        else:
            self.showItem(None)

        self.updateButtons()

    # ("map", map) or ("item", id) of the selected node, or None
    def selected(self):
        n = self.tree.GetSelection()

        return self.nodes.get(n) if n.IsOk() else None

    def selectedItem(self):
        sel = self.selected()

        return self.bible.get(sel[1]) if sel and sel[0] == "item" else None

    # the map of the selected node
    def selectedMap(self):
        sel = self.selected()

        if not sel:
            return None

        return sel[1] if sel[0] == "map" else self.bible.get(sel[1]).map

    def updateButtons(self):
        sel = self.selected()
        self.newBtn.Enable(bool(sel))
        self.childBtn.Enable(bool(sel and sel[0] == "item"))
        self.renameBtn.Enable(bool(sel and sel[0] == "item"))
        self.deleteBtn.Enable(bool(sel and sel[0] == "item"))

    def OnSelChanged(self, event):
        self.updateButtons()

        if self.bible is not None:
            self.showItem(self.selectedItem())

    # run fn, showing what the film refused instead of crashing
    def guard(self, fn, *args):
        try:
            return fn(*args)
        except Exception as e:
            wx.MessageBox(str(e), _("Bible"), wx.OK, self)

            return None

    def askName(self, title, value=""):
        dlg = wx.TextEntryDialog(self, _("Name:"), title, value)
        name = dlg.GetValue().strip() if dlg.ShowModal() == wx.ID_OK else ""
        dlg.Destroy()

        return name or None

    def OnNew(self, event=None):
        map_ = self.selectedMap()

        if map_ is None:
            return

        name = self.askName(_("New item in %s") % _(MAP_LABELS[map_]))

        if name:
            it = self.guard(self.bible.create, map_, name, None, "creator")

            if it:
                self.refresh(it.id)

    def OnNewChild(self, event=None):
        parent = self.selectedItem()

        if parent is None:
            return

        name = self.askName(_("New item inside %s") % parent.name)

        if name:
            it = self.guard(self.bible.create, parent.map, name, parent, "creator")

            if it:
                self.refresh(it.id)

    def OnRename(self, event=None):
        it = self.selectedItem()

        if it is None:
            return

        name = self.askName(_("Rename"), it.name)

        if name and name != it.name:
            self.guard(self.bible.rename, it, name, "creator")
            self.refresh(it.id)

    def OnDelete(self, event=None):
        it = self.selectedItem()

        if it is None:
            return

        kids = len(self.descendants(it))
        msg = _("Delete %s with its files?") % it.name

        if kids:
            msg += "\n" + _("Its %d child items are deleted too.") % kids

        scenes = sorted(self.bible.scenes(it))

        if scenes:
            msg += "\n" + _("Scenes that use it: %s") % ", ".join(scenes)

        if (
            wx.MessageBox(msg, _("Delete"), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING, self)
            == wx.YES
        ):
            self.guard(self.bible.delete, it, "creator")
            self.refresh(it.map)

    def descendants(self, it):
        out = []

        for c in self.bible.children(it.map, it.id):
            out.append(c)
            out.extend(self.descendants(c))

        return out

    def OnItemMenu(self, event):
        self.tree.SelectItem(event.GetItem())
        menu = wx.Menu()

        for label, fn in self.menuItems():
            if label is None:
                menu.AppendSeparator()

                continue

            mi = menu.Append(-1, label)
            self.Bind(wx.EVT_MENU, fn, id=mi.GetId())

        self.PopupMenu(menu)
        menu.Destroy()

    # (label, handler) of the right-click menu; None label: a separator
    def menuItems(self):
        items = [(_("New item"), self.OnNew)]

        if self.selectedItem():
            items += [
                (_("New child item"), self.OnNewChild),
                (_("Rename"), self.OnRename),
                (_("Move to the top level"), self.OnMoveTop),
                (_("Copy"), self.OnCopy),
                (_("Copy to another film..."), self.OnCopyToFilm),
                (None, None),
                (_("Delete"), self.OnDelete),
            ]

        return items

    def OnMoveTop(self, event=None):
        it = self.selectedItem()

        if it and it.parent:
            self.guard(self.bible.move, it, None, "creator")
            self.refresh(it.id)

    def OnBeginDrag(self, event):
        key = self.nodes.get(event.GetItem())

        if key and key[0] == "item":
            self.dragId = key[1]
            event.Allow()

    # drop an item on another item of its map: it becomes its child; on its
    # map: it goes to the top level
    def OnEndDrag(self, event):
        dragId, self.dragId = self.dragId, None
        target = event.GetItem()

        if dragId is None or not target.IsOk():
            return

        it = self.bible.get(dragId)
        key = self.nodes.get(target)

        if key[0] == "map":
            parent = None

            if key[1] != it.map or it.parent is None:
                return
        else:
            parent = self.bible.get(key[1])

            if parent.id == it.parent:
                return

        self.guard(self.bible.move, it, parent, "creator")
        self.refresh(it.id)

    # the open script's Screenplay, and the cursor
    def script(self):
        ctrl = self.frame.panel.ctrl

        return ctrl.sp

    # the script's links to the bible (film-bible/links): each command
    # shows what it would do, and does only what the creator checks
    def OnScriptMenu(self, event=None):
        menu = wx.Menu()

        for label, fn in self.scriptMenuItems():
            mi = menu.Append(-1, label)
            self.Bind(wx.EVT_MENU, fn, id=mi.GetId())

        self.PopupMenu(menu)
        menu.Destroy()

    def scriptMenuItems(self):
        return [
            (_("Link scenes to sets..."), self.OnLinkSets),
            (_("Find characters..."), self.OnFindCharacters),
            (_("Find props..."), self.OnFindProps),
            (_("Wardrobe gaps..."), self.OnWardrobeGaps),
            (_("Review all..."), self.OnReviewAll),
        ]

    # import-to-film/flow/2: sets, characters and props in one review; new
    # items unticked, as in the other From script commands
    def OnReviewAll(self, event=None):
        import trelby.biblereviewdlg as biblereviewdlg

        sp = self.script()
        made = self.guard(
            biblereviewdlg.review, self, self.bible, sp, False, True, self.noteUnnumbered(sp).strip()
        )

        if made == {}:
            wx.MessageBox(_("Nothing to do: the bible already matches the script."),
                          _("Bible"), wx.OK, self)

        self.changed()

    # warn if the script has scenes with no number yet: those are left out
    # until a save numbers them
    def unnumbered(self, sp):
        import trelby.scenenumbers as scenenumbers

        return sum(1 for _l, n in scenenumbers.scenesOf(sp) if not n)

    # ask which of choices (labels) to do, those in checked ticked; the
    # indexes chosen, or None if cancelled
    def choose(self, title, text, choices, checked):
        if not choices:
            wx.MessageBox(_("Nothing to do: the bible already matches the script."), title, wx.OK, self)

            return None

        dlg = wx.MultiChoiceDialog(self, text, title, choices)
        dlg.SetSelections(checked)
        ret = dlg.GetSelections() if dlg.ShowModal() == wx.ID_OK else None
        dlg.Destroy()

        return ret

    def noteUnnumbered(self, sp):
        n = self.unnumbered(sp)

        return (
            "\n" + _("%d scenes have no number yet and are left out: save the script first.") % n
            if n
            else ""
        )

    # links/1: scene headings -> sets
    def OnLinkSets(self, event=None):
        sp = self.script()
        links, unknown = biblelinks.setPlan(self.bible, sp)
        choices = [_("Link scene %s to %s") % (n, it.name) for it, n in links]
        news = list(unknown.items())
        choices += [
            _("New set %s (scenes %s)") % (loc, ", ".join(nums)) for loc, nums in news
        ]
        sel = self.choose(
            _("Link scenes to sets"),
            _("From the scene headings. A new set is made only if you check it.")
            + self.noteUnnumbered(sp),
            choices,
            list(range(len(links))),
        )

        if sel is None:
            return

        chosenLinks = [links[i] for i in sel if i < len(links)]
        chosenNew = dict(news[i - len(links)] for i in sel if i >= len(links))
        self.guard(biblelinks.applyLinks, self.bible, chosenLinks)
        self.guard(biblelinks.createSets, self.bible, chosenNew)
        self.changed()

    # the bible changed under the tree: rebuild it and the scene line
    def changed(self):
        self.refresh()
        self.sceneShown = None
        self.showScene(self.script())

    # show the bible's items in the scene holding sp's cursor
    def showScene(self, sp):
        if self.bible is None or not self.IsShown():
            return

        num = biblelinks.sceneAt(sp, sp.line)
        text = ""

        if num:
            parts = []

            for map_ in bible.MAPS:
                items = biblelinks.itemsInScene(self.bible, num).get(map_)

                if items:
                    parts.append(
                        "%s: %s" % (_(MAP_LABELS[map_]), ", ".join(it.name for it in items))
                    )

            text = _("Scene %s") % num + (" - " + "; ".join(parts) if parts else "")

        self.thisSceneBtn.Enable(bool(num))

        if (num, text) != self.sceneShown:
            self.sceneShown = (num, text)
            self.sceneText.SetLabel(text)
            self.sceneText.Wrap(max(self.GetSize().width - 12, 100))
            self.Layout()

    # links/6: tick every set, character and prop in the cursor's scene;
    # OK links and unlinks the changes only
    def OnThisScene(self, event=None):
        sp = self.script()
        num = biblelinks.sceneAt(sp, sp.line)

        if self.bible is None or not num:
            return

        self.form.commitFocused()
        rows = bibleedit.sceneItemChoices(self.bible)

        if not rows:
            wx.MessageBox(_("There are no sets, characters or props in the bible yet."),
                          _("Bible"), wx.OK, self)

            return

        linked = bibleedit.sceneItems(self.bible, num)
        labels = [
            "%s: %s%s" % (_(MAP_LABELS[it.map]), "    " * depth, it.name) for it, depth in rows
        ]
        dlg = wx.MultiChoiceDialog(self, _("What is in scene %s:") % num, _("Bible"), labels)
        dlg.SetSelections([i for i, (it, _d) in enumerate(rows) if it.id in linked])

        if dlg.ShowModal() == wx.ID_OK:
            ids = [rows[i][0].id for i in dlg.GetSelections()]
            self.guard(bibleedit.setSceneItems, self.bible, num, ids)
            self.changed()
            self.form.build()

        dlg.Destroy()

    # links/2: runs of capitalized words in Action -> props
    def OnFindProps(self, event=None):
        sp = self.script()
        links, new = biblelinks.propPlan(self.bible, sp, sp.line, sp.column)
        news = list(new.items())
        choices = [_("Link %s in scene %s") % (it.name, n) for it, n in links]
        choices += [
            _("New prop %s (scenes %s)") % (run, ", ".join(nums)) for run, nums in news
        ]
        sel = self.choose(
            _("Find props"),
            _("Capitalized words in Action. A new prop is made only if you check it.")
            + self.noteUnnumbered(sp),
            choices,
            list(range(len(links))),
        )

        if sel is None:
            return

        chosenLinks = [links[i] for i in sel if i < len(links)]
        chosenNew = dict(news[i - len(links)] for i in sel if i >= len(links))
        self.guard(biblelinks.applyLinks, self.bible, chosenLinks)
        self.guard(biblelinks.createProps, self.bible, chosenNew)

        # the ones not made can be marked "not a prop" once for the film
        rest = [run for run, _n in news if run not in chosenNew]

        if rest:
            dlg = wx.MultiChoiceDialog(
                self,
                _("Mark any of these as not a prop, for the whole film?"),
                _("Find props"),
                rest,
            )

            if dlg.ShowModal() == wx.ID_OK and dlg.GetSelections():
                words = [rest[i] for i in dlg.GetSelections()]
                self.guard(biblelinks.markNotProps, self.bible, words)

            dlg.Destroy()

        self.changed()

    # links/3: characters in a scene with no wardrobe linked to them there
    def OnWardrobeGaps(self, event=None):
        sp = self.script()
        gaps = biblelinks.wardrobeGaps(self.bible, sp)

        if gaps:
            lines = [
                _("Scene %s: %s") % (n, self.bible.get(cid).name) for n, cid in gaps
            ]
            text = (
                _("These characters have no wardrobe in these scenes (a gap, not an error):")
                + "\n\n"
                + "\n".join(lines)
            )
        else:
            text = _("Every character the bible knows has wardrobe in every scene.")

        text += self.noteUnnumbered(sp)
        misc.showText(self, text, _("Wardrobe gaps"))

    # links/4: a copy next to the item, named "<name> copy" so the script's
    # links never mistake it for the original; it gets a new id and no
    # scenes, and the creator is told where the original is used
    def OnCopy(self, event=None):
        it = self.selectedItem()

        if it is None:
            return

        parent = self.bible.get(it.parent) if it.parent else None
        copy = self.guard(
            biblelinks.copyItem, self.bible, it, self.bible, parent, "creator",
            _("%s copy") % it.name,
        )

        if copy:
            self.warnUnlinked(it, copy)
            self.changed()
            self.refresh(copy.id)

    # links/4: copy the item, its files and children, into another film's
    # bible; scene numbers name scenes only in their own film, so the copy
    # has none
    def OnCopyToFilm(self, event=None):
        import trelby.film as film

        it = self.selectedItem()

        if it is None:
            return

        dlg = wx.DirDialog(self, _("Film to copy %s into") % it.name)
        root = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
        dlg.Destroy()

        if root is None:
            return

        # a film open in the window is copied into through its own bible,
        # so its tab sees the copy
        of = self.frame.openFilms.at(root)

        try:
            other = of.bible if of else bible.Bible(film.Film.open(root))
        except Exception as e:
            wx.MessageBox(str(e), _("Bible"), wx.OK, self)

            return

        if os.path.realpath(other.film.root) == os.path.realpath(self.bible.film.root):
            self.OnCopy()

            return

        copy = self.guard(biblelinks.copyItem, self.bible, it, other, None, "creator")

        if copy:
            wx.MessageBox(
                _("%s was copied to %s as %s, with its files and child items, "
                  "and without its scenes.") % (it.name, root, copy.id),
                _("Bible"),
                wx.OK,
                self,
            )

    def warnUnlinked(self, it, copy):
        scenes = biblelinks.usedIn(self.bible, it)

        if scenes:
            wx.MessageBox(
                _("%s is in no scene. %s, the original, is used in scenes %s: "
                  "link the copy to the ones it replaces it in.")
                % (copy.name, it.name, ", ".join(scenes)),
                _("Bible"),
                wx.OK,
                self,
            )

    # links/5: the speakers of the script -> characters
    def OnFindCharacters(self, event=None):
        sp = self.script()
        links, new = biblelinks.characterPlan(self.bible, sp)
        news = list(new.items())
        choices = [_("Link %s to scene %s") % (it.name, n) for it, n in links]
        choices += [
            _("New character %s (scenes %s)") % (name, ", ".join(nums))
            for name, nums in news
        ]
        sel = self.choose(
            _("Find characters"),
            _("The characters who speak. A new character is made only if you check it.")
            + self.noteUnnumbered(sp),
            choices,
            list(range(len(links))),
        )

        if sel is None:
            return

        chosenLinks = [links[i] for i in sel if i < len(links)]
        chosenNew = dict(news[i - len(links)] for i in sel if i >= len(links))
        self.guard(biblelinks.applyLinks, self.bible, chosenLinks)
        self.guard(biblelinks.createCharacters, self.bible, chosenNew)
        self.changed()
