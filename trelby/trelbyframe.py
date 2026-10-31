# -*- coding: iso-8859-1 -*-

import copy
import os
import os.path
import signal
from functools import partial

import wx
import wx.svg

import trelby
import trelby.charmapdlg as charmapdlg
import trelby.commandsdlg as commandsdlg
import trelby.annotationdlg as annotationdlg
import trelby.annotations as annotations
import trelby.biblepanel as biblepanel
import trelby.biblereviewdlg as biblereviewdlg
import trelby.config as config
import trelby.film as film
import trelby.frontmatter as frontmatter
import trelby.importfilm as importfilm
import trelby.importreportdlg as importreportdlg
import trelby.manual as manual
import trelby.misc as misc
import trelby.namesdlg as namesdlg
import trelby.openfilms as openfilms
import trelby.relinkdlg as relinkdlg
import trelby.review as review
import trelby.reviewdlg as reviewdlg
import trelby.scriptsettings as scriptsettings
import trelby.spellcheckcfgdlg as spellcheckcfgdlg
import trelby.splash as splash
import trelby.sync as sync
import trelby.syncdlg as syncdlg
import trelby.util as util
from trelby.ids import *
from trelby.trelbypanel import MyPanel


class MyFrame(wx.Frame):

    def __init__(self, parent, id, title, gd, myApp):
        wx.Frame.__init__(self, parent, id, title, name="Trelby")

        if misc.isUnix:
            # automatically reaps zombies
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        self.clipboard = None
        self.showFormatting = False
        self.gd = gd
        self.myApp = myApp

        # every film opened or made (file-format/layout/4); a tab belongs to
        # the film whose script it holds (bugs/editor/20)
        self.openFilms = openfilms.OpenFilms()

        # the current tab's film, a film.Film, or None
        self.film = None

        # its bible (film-bible), a bible.Bible, or None
        self.bible = None

        # its annotations (fountain-native/notes/1), an
        # annotations.Annotations, or None; shown on the script when
        # showAnnotations
        self.annotations = None
        self.showAnnotations = False

        # called with no arguments when self.film changes (the bible panel)
        self.filmListeners = []

        self.SetSizeHints(gd.cvars.getMin("width"), gd.cvars.getMin("height"))

        self.Move(gd.posX, gd.posY)
        self.SetSize(wx.Size(gd.width, gd.height))

        util.removeTempFiles(misc.tmpPrefix)

        self.mySetIcons()
        # self.allocIds()

        fileMenu = wx.Menu()
        fileMenu.Append(ID_FILE_NEW, "(&N) " + _("New") + "\tCTRL-N")
        fileMenu.Append(ID_FILE_OPEN, "(&O) " + _("Open") + "...\tCTRL-O")
        fileMenu.Append(ID_FILE_SAVE, "(&S) " + _("Save") + "\tCTRL-S")
        fileMenu.Append(ID_FILE_SAVE_AS, "(&A) " + _("Save As") + "...")
        fileMenu.Append(ID_FILE_CLOSE, "(&C) " + _("Close\tCTRL-W"))
        fileMenu.Append(ID_FILE_REVERT, "(&R) " + _("Revert"))
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_FILE_NEW_FILM, _("New film") + "...")
        fileMenu.Append(ID_FILE_OPEN_FILM, _("Open film") + "...")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_FILE_IMPORT, "(&I) " + _("Import") + "...")
        fileMenu.Append(ID_FILE_IMPORT_FILM, _("Import into film") + "...")
        fileMenu.Append(ID_FILE_EXPORT, "(&E) " + _("Export") + "...")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_FILE_PRINT, "(&P) " + _("Print (via PDF)") + "\tCTRL-P")
        fileMenu.AppendSeparator()

        tmp = wx.Menu()

        tmp.Append(ID_SETTINGS_CHANGE, "(&C) " + _("Change") + "...")
        tmp.AppendSeparator()
        tmp.Append(ID_SETTINGS_LOAD, _("Load") + "...")
        tmp.Append(ID_SETTINGS_SAVE_AS, _("Save as") + "...")
        tmp.AppendSeparator()
        tmp.Append(ID_SETTINGS_SC_DICT, "(&S) " + _("Spell checker dictionary") + "...")
        settingsMenu = tmp

        fileMenu.Append(ID_FILE_SETTINGS, "(&t) " + _("Settings"), tmp)

        fileMenu.AppendSeparator()
        # "most recently used" list comes in here
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_FILE_EXIT, "(x) " + _("Exit") + "\tCTRL-Q")

        editMenu = wx.Menu()
        editMenu.Append(ID_EDIT_UNDO, "(&U) " + _("Undo") + "\tCTRL-Z")
        editMenu.Append(ID_EDIT_REDO, "(&R) " + _("Redo") + "\tCTRL-Y")
        editMenu.AppendSeparator()
        editMenu.Append(ID_EDIT_CUT, "(&t) " + _("Cut") + "\tCTRL-X")
        editMenu.Append(ID_EDIT_COPY, "(&C) " + _("Copy") + "\tCTRL-C")
        editMenu.Append(ID_EDIT_PASTE, "(&P) " + _("Paste") + "\tCTRL-V")
        editMenu.AppendSeparator()

        tmp = wx.Menu()
        tmp.Append(ID_EDIT_COPY_TO_CB, "(&U) " + _("Unformatted"))
        tmp.Append(ID_EDIT_COPY_TO_CB_FMT, "(&F) " + _("Formatted"))

        editMenu.Append(ID_EDIT_COPY_SYSTEM, "(&o) " + _("Copy (system)"), tmp)
        editMenu.Append(ID_EDIT_PASTE_FROM_CB, "(&a) " + _("Paste (system)"))
        editMenu.AppendSeparator()
        editMenu.Append(ID_EDIT_SELECT_SCENE, "(&S) " + _("Select scene"))
        editMenu.Append(ID_EDIT_SELECT_ALL, "(&l) " + _("Select all"))
        editMenu.Append(ID_EDIT_GOTO_PAGE, "(&G) " + _("Goto page") + "...\tCTRL-G")
        editMenu.Append(ID_EDIT_GOTO_SCENE, "(&e) " + _("Goto scene") + "...\tALT-G")
        editMenu.AppendSeparator()
        editMenu.Append(ID_EDIT_INSERT_NBSP, _("Insert non-breaking space"))
        editMenu.AppendSeparator()
        editMenu.Append(ID_EDIT_FIND, "(&F) " + _("Find && Replace") + "...\tCTRL-F")
        editMenu.AppendSeparator()
        editMenu.Append(ID_EDIT_DELETE_ELEMENTS, "(&D) " + _("Delete elements") + "...")

        viewMenu = wx.Menu()
        viewMenu.AppendRadioItem(ID_VIEW_STYLE_DRAFT, "(&D) " + _("Draft"))
        viewMenu.AppendRadioItem(ID_VIEW_STYLE_LAYOUT, "(&L) " + _("Layout"))
        viewMenu.AppendRadioItem(
            ID_VIEW_STYLE_SIDE_BY_SIDE, "(&S) " + _("Side by side")
        )
        viewMenu.AppendCheckItem(ID_SHOW_HIDE_TOOLBAR, "(&S) " + _("Show/Hide Toolbar"))

        if gd.viewMode == gd.VIEWMODE_DRAFT:
            viewMenu.Check(ID_VIEW_STYLE_DRAFT, True)
        elif gd.viewMode == gd.VIEWMODE_LAYOUT:
            viewMenu.Check(ID_VIEW_STYLE_LAYOUT, True)
        else:
            viewMenu.Check(ID_VIEW_STYLE_SIDE_BY_SIDE, True)

        viewMenu.AppendSeparator()
        viewMenu.AppendCheckItem(
            ID_VIEW_SHOW_FORMATTING, "(&S) " + _("Show formatting")
        )
        viewMenu.AppendCheckItem(ID_VIEW_BIBLE, "(&B) " + _("Bible") + "\tCTRL-SHIFT-B")
        viewMenu.AppendCheckItem(
            ID_VIEW_ANNOTATIONS, "(&A) " + _("Show annotations") + "\tCTRL-SHIFT-N"
        )
        viewMenu.AppendCheckItem(ID_VIEW_DARK_THEME, "(&T) " + _("Dark theme"))
        viewMenu.Check(ID_VIEW_DARK_THEME, gd.cfgGl.theme == config.THEME_DARK)
        viewMenu.Append(ID_VIEW_FULL_SCREEN, "(&F) " + _("Fullscreen") + "\tF11")

        scriptMenu = wx.Menu()
        scriptMenu.Append(ID_SCRIPT_FIND_ERROR, "(&F) " + _("Find next error"))
        scriptMenu.Append(ID_SCRIPT_PAGINATE, "(&P) " + _("Paginate"))
        scriptMenu.Append(
            ID_SCRIPT_RENUMBER, "(&R) " + _("Renumber all scenes") + "..."
        )
        scriptMenu.AppendSeparator()
        scriptMenu.Append(ID_SCRIPT_ANNOTATE, _("Annotate") + "...\tCTRL-SHIFT-A")
        scriptMenu.Append(ID_SCRIPT_ANNOTATIONS_HERE, _("Annotations here") + "...")
        scriptMenu.Append(ID_SCRIPT_ANNOTATIONS_UNATTACHED, _("Unattached annotations") + "...")
        scriptMenu.Append(ID_SCRIPT_SYNC, _("Sync to spec") + "...\tF5")
        scriptMenu.Append(ID_SCRIPT_REVIEW, _("Review proposals") + "...")
        scriptMenu.AppendSeparator()
        scriptMenu.Append(
            ID_SCRIPT_AUTO_COMPLETION, "(&A) " + _("Auto-completion") + "..."
        )
        scriptMenu.Append(ID_SCRIPT_HEADERS, "(&H) " + _("Headers") + "...")
        scriptMenu.Append(ID_SCRIPT_LOCATIONS, "(&L) " + _("Locations") + "...")
        scriptMenu.Append(ID_SCRIPT_TITLES, "(&T) " + _("Title pages") + "...")
        scriptMenu.Append(ID_SCRIPT_SC_DICT, "(&S) " + _("Spell checker dictionary..."))
        scriptMenu.AppendSeparator()

        tmp = wx.Menu()

        tmp.Append(ID_SCRIPT_SETTINGS_CHANGE, "(&C) " + _("Change") + "...")
        tmp.AppendSeparator()
        tmp.Append(ID_SCRIPT_SETTINGS_LOAD, "(&L) " + _("Load") + "...")
        tmp.Append(ID_SCRIPT_SETTINGS_SAVE_AS, "(&S) " + _("Save as") + "...")
        scriptMenu.Append(ID_SCRIPT_SETTINGS, "(&S) " + _("Settings"), tmp)
        scriptSettingsMenu = tmp

        reportsMenu = wx.Menu()
        reportsMenu.Append(ID_REPORTS_SCRIPT_REP, "(&r) " + _("Script report"))
        reportsMenu.Append(
            ID_REPORTS_LOCATION_REP, "(&L) " + _("Location report") + "..."
        )
        reportsMenu.Append(ID_REPORTS_SCENE_REP, "(&S) " + _("Scene report") + "...")
        reportsMenu.Append(
            ID_REPORTS_CHARACTER_REP, "(&C) " + _("Character report") + "..."
        )
        reportsMenu.Append(
            ID_REPORTS_DIALOGUE_CHART, "(&D) " + _("Dialogue chart") + "..."
        )

        toolsMenu = wx.Menu()
        toolsMenu.Append(ID_TOOLS_SPELL_CHECK, "(&S) " + _("Spell checker") + "...")
        toolsMenu.Append(ID_TOOLS_NAME_DB, "(&N) " + _("Name database") + "...")
        toolsMenu.Append(ID_TOOLS_CHARMAP, "(&C) " + _("Character map") + "...")
        toolsMenu.Append(
            ID_TOOLS_COMPARE_SCRIPTS, "(&o) " + _("Compare scripts") + "..."
        )
        toolsMenu.Append(
            ID_TOOLS_WATERMARK, "(&G) " + _("Generate watermarked PDFs") + "..."
        )

        helpMenu = wx.Menu()
        helpMenu.Append(ID_HELP_COMMANDS, "(&C) " + _("Commands") + "...")
        helpMenu.Append(ID_HELP_MANUAL, "(&M) " + _("Manual"))
        helpMenu.AppendSeparator()
        helpMenu.Append(ID_HELP_ABOUT, "(&A) " + _("About") + "...")

        self.menuBar = wx.MenuBar()
        self.menuBar.Append(fileMenu, "(&F) " + _("File"))
        self.menuBar.Append(editMenu, "(&E) " + _("Edit"))
        self.menuBar.Append(viewMenu, "(&V) " + _("View"))
        self.menuBar.Append(scriptMenu, "(&i) " + _("Script"))
        self.menuBar.Append(reportsMenu, "(&R) " + _("Reports"))
        self.menuBar.Append(toolsMenu, "(&l) " + _("Tools"))
        self.menuBar.Append(helpMenu, "(&H) " + _("Help"))
        self.SetMenuBar(self.menuBar)

        self.toolBar = self.CreateToolBar(wx.TB_VERTICAL)

        def addTB(id, iconFilename, toolTip):
            filepath = misc.getFullPath(("trelby/resources/%s" % iconFilename))

            # neat hack to change the color of the SVG
            with open(filepath, "r") as svg_file:
                svg_content = svg_file.read()

            if wx.SystemSettings.GetAppearance().IsDark():
                svg_content = svg_content.replace("fill:#000000", "fill:#CCCCCC")
            svg_content = svg_content.encode()

            # svg_image = wx.svg.SVGimage.CreateFromBytes(svg_content)
            bitmap = wx.BitmapBundle.FromSVG(svg_content, wx.Size(32, 32))

            self.toolBar.AddTool(
                id,
                "",
                bitmap,
                shortHelp=toolTip,
            )

        addTB(ID_FILE_NEW, "new.svg", _("New script"))
        addTB(ID_FILE_OPEN, "open.svg", _("Open Script") + "..")
        addTB(ID_FILE_SAVE, "save.svg", _("Save") + "..")
        addTB(ID_FILE_SAVE_AS, "saveas.svg", _("Save as") + "..")
        addTB(ID_FILE_CLOSE, "close.svg", _("Close Script"))
        addTB(ID_TOOLBAR_SCRIPTSETTINGS, "scrset.svg", _("Script settings"))
        addTB(ID_FILE_PRINT, "pdf.svg", _("Print (via PDF)"))

        self.toolBar.AddSeparator()

        addTB(ID_FILE_IMPORT, "import.svg", _("Import a text script"))
        addTB(ID_FILE_EXPORT, "export.svg", _("Export script"))

        self.toolBar.AddSeparator()

        addTB(ID_EDIT_UNDO, "undo.svg", _("Undo"))
        addTB(ID_EDIT_REDO, "redo.svg", _("Redo"))

        self.toolBar.AddSeparator()

        addTB(ID_EDIT_FIND, "find.svg", _("Find / Replace"))
        addTB(ID_SCRIPT_SYNC, "sync.svg", _("Sync to spec"))
        addTB(ID_TOOLBAR_VIEWS, "view.svg", _("View mode"))
        addTB(ID_TOOLBAR_REPORTS, "report.svg", _("Script reports"))
        addTB(ID_TOOLBAR_TOOLS, "tools.svg", _("Tools"))
        addTB(ID_TOOLBAR_SETTINGS, "settings.svg", _("Global settings"))

        self.toolBar.SetBackgroundColour(gd.cfgGui.tabBarBgColor)
        self.toolBar.Realize()

        self.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vsizer)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.noFSBtn = misc.MyFSButton(self, -1, self.getCfgGui)
        self.noFSBtn.SetToolTip(_("Exit fullscreen"))
        self.noFSBtn.Show(False)
        hsizer.Add(self.noFSBtn)

        self.Bind(wx.EVT_BUTTON, self.ToggleFullscreen, id=self.noFSBtn.GetId())

        self.tabCtrl = misc.MyTabCtrl(self, -1, self.getCfgGui)
        hsizer.Add(self.tabCtrl, 1, wx.EXPAND)

        self.statusCtrl = misc.MyStatus(self, -1, self.getCfgGui)
        self.statusCtrl.setZoom(gd.cfgGl.zoom)
        self.statusCtrl.setZoomFuncs(self.OnZoomOut, self.OnZoomReset, self.OnZoomIn)
        self.statusCtrl.Bind(wx.EVT_SET_FOCUS, self.OnStatusFocus)
        hsizer.Add(self.statusCtrl)

        vsizer.Add(hsizer, 0, wx.EXPAND)

        # the bible panel and the scripts side by side (film-bible/tree/1);
        # unsplit while the bible is hidden
        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetMinimumPaneSize(120)
        self.biblePanel = biblepanel.BiblePanel(self.splitter, -1, self)
        tmp = misc.MyTabCtrl2(self.splitter, -1, self.tabCtrl)
        self.scriptsPane = tmp
        self.splitter.Initialize(tmp)
        self.biblePanel.Hide()
        vsizer.Add(self.splitter, 1, wx.EXPAND)

        vsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)

        gd.mru.useMenu(fileMenu, 14)

        self.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.OnMenuHighlight)

        self.tabCtrl.setPageChangedFunc(self.OnPageChange)

        # see OnRightDown
        self.rightClickMenu = wx.Menu()
        self.rightClickMenuWithCut = wx.Menu()

        for m in (self.rightClickMenu, self.rightClickMenuWithCut):
            tmp = wx.Menu()

            tmp.Append(ID_ELEM_TO_SCENE, "(&S) " + _("Scene"))
            tmp.Append(ID_ELEM_TO_ACTION, "(&A) " + _("Action"))
            tmp.Append(ID_ELEM_TO_CHARACTER, "(&C) " + _("Character"))
            tmp.Append(ID_ELEM_TO_PAREN, "(&P) " + _("Parenthetical"))
            tmp.Append(ID_ELEM_TO_DIALOGUE, "(&D) " + _("Dialogue"))
            tmp.Append(ID_ELEM_TO_TRANSITION, "(&T) " + _("Transition"))
            tmp.Append(ID_ELEM_TO_SHOT, "(&o) " + _("Shot"))
            tmp.Append(ID_ELEM_TO_ACTBREAK, "(&b) " + _("Act break"))
            tmp.Append(ID_ELEM_TO_NOTE, "(&N) " + _("Note"))

            m.AppendSubMenu(tmp, _("Element type"))
            m.AppendSeparator()

            if m is self.rightClickMenuWithCut:
                m.Append(ID_EDIT_CUT, _("Cut"))
                m.Append(ID_EDIT_COPY, _("Copy"))

            m.Append(ID_EDIT_PASTE, _("Paste"))

            self.Bind(wx.EVT_MENU, self.OnNewScript, id=ID_FILE_NEW)
            self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_FILE_OPEN)
            self.Bind(wx.EVT_MENU, self.OnNewFilm, id=ID_FILE_NEW_FILM)
            self.Bind(wx.EVT_MENU, self.OnOpenFilm, id=ID_FILE_OPEN_FILM)
            self.Bind(wx.EVT_MENU, self.OnSave, id=ID_FILE_SAVE)
            self.Bind(wx.EVT_MENU, self.OnSaveScriptAs, id=ID_FILE_SAVE_AS)
            self.Bind(wx.EVT_MENU, self.OnImportScript, id=ID_FILE_IMPORT)
            self.Bind(wx.EVT_MENU, self.OnImportIntoFilm, id=ID_FILE_IMPORT_FILM)
            self.Bind(wx.EVT_MENU, self.OnExportScript, id=ID_FILE_EXPORT)
            self.Bind(wx.EVT_MENU, self.OnCloseScript, id=ID_FILE_CLOSE)
            self.Bind(wx.EVT_MENU, self.OnRevertScript, id=ID_FILE_REVERT)
            self.Bind(wx.EVT_MENU, self.OnPrint, id=ID_FILE_PRINT)
            self.Bind(wx.EVT_MENU, self.OnSettings, id=ID_SETTINGS_CHANGE)
            self.Bind(wx.EVT_MENU, self.OnLoadSettings, id=ID_SETTINGS_LOAD)
            self.Bind(wx.EVT_MENU, self.OnSaveSettingsAs, id=ID_SETTINGS_SAVE_AS)
            self.Bind(
                wx.EVT_MENU, self.OnSpellCheckerDictionaryDlg, id=ID_SETTINGS_SC_DICT
            )
            self.Bind(wx.EVT_MENU, self.OnExit, id=ID_FILE_EXIT)
            self.Bind(wx.EVT_MENU, self.OnUndo, id=ID_EDIT_UNDO)
            self.Bind(wx.EVT_MENU, self.OnRedo, id=ID_EDIT_REDO)
            self.Bind(wx.EVT_MENU, self.OnCut, id=ID_EDIT_CUT)
            self.Bind(wx.EVT_MENU, self.OnCopy, id=ID_EDIT_COPY)
            self.Bind(wx.EVT_MENU, self.OnPaste, id=ID_EDIT_PASTE)
            self.Bind(wx.EVT_MENU, self.OnCopySystemCb, id=ID_EDIT_COPY_TO_CB)
            self.Bind(
                wx.EVT_MENU, self.OnCopySystemCbFormatted, id=ID_EDIT_COPY_TO_CB_FMT
            )
            self.Bind(wx.EVT_MENU, self.OnPasteSystemCb, id=ID_EDIT_PASTE_FROM_CB)
            self.Bind(wx.EVT_MENU, self.OnSelectScene, id=ID_EDIT_SELECT_SCENE)
            self.Bind(wx.EVT_MENU, self.OnSelectAll, id=ID_EDIT_SELECT_ALL)
            self.Bind(wx.EVT_MENU, self.OnGotoPage, id=ID_EDIT_GOTO_PAGE)
            self.Bind(wx.EVT_MENU, self.OnGotoScene, id=ID_EDIT_GOTO_SCENE)
            self.Bind(wx.EVT_MENU, self.OnInsertNbsp, id=ID_EDIT_INSERT_NBSP)
            self.Bind(wx.EVT_MENU, self.OnFind, id=ID_EDIT_FIND)
            self.Bind(wx.EVT_MENU, self.OnDeleteElements, id=ID_EDIT_DELETE_ELEMENTS)
            self.Bind(wx.EVT_MENU, self.OnViewModeChange, id=ID_VIEW_STYLE_DRAFT)
            self.Bind(wx.EVT_MENU, self.ShowHideToolbar, id=ID_SHOW_HIDE_TOOLBAR)
            self.Bind(wx.EVT_MENU, self.OnViewModeChange, id=ID_VIEW_STYLE_LAYOUT)
            self.Bind(wx.EVT_MENU, self.OnViewModeChange, id=ID_VIEW_STYLE_SIDE_BY_SIDE)
            self.Bind(wx.EVT_MENU, self.OnShowFormatting, id=ID_VIEW_SHOW_FORMATTING)
            self.Bind(wx.EVT_MENU, self.OnDarkTheme, id=ID_VIEW_DARK_THEME)
            self.Bind(wx.EVT_MENU, self.OnViewBible, id=ID_VIEW_BIBLE)
            self.Bind(wx.EVT_MENU, self.OnViewAnnotations, id=ID_VIEW_ANNOTATIONS)
            self.Bind(wx.EVT_MENU, self.OnAnnotate, id=ID_SCRIPT_ANNOTATE)
            self.Bind(wx.EVT_MENU, self.OnSyncToSpec, id=ID_SCRIPT_SYNC)
            self.Bind(wx.EVT_MENU, self.OnReview, id=ID_SCRIPT_REVIEW)
            self.Bind(wx.EVT_MENU, self.OnAnnotationsHere, id=ID_SCRIPT_ANNOTATIONS_HERE)
            self.Bind(
                wx.EVT_MENU, self.OnAnnotationsUnattached, id=ID_SCRIPT_ANNOTATIONS_UNATTACHED
            )
            self.Bind(wx.EVT_MENU, self.ToggleFullscreen, id=ID_VIEW_FULL_SCREEN)
            self.Bind(wx.EVT_MENU, self.OnFindNextError, id=ID_SCRIPT_FIND_ERROR)
            self.Bind(wx.EVT_MENU, self.OnPaginate, id=ID_SCRIPT_PAGINATE)
            self.Bind(wx.EVT_MENU, self.OnRenumberScenes, id=ID_SCRIPT_RENUMBER)
            self.Bind(
                wx.EVT_MENU, self.OnAutoCompletionDlg, id=ID_SCRIPT_AUTO_COMPLETION
            )
            self.Bind(wx.EVT_MENU, self.OnHeadersDlg, id=ID_SCRIPT_HEADERS)
            self.Bind(wx.EVT_MENU, self.OnLocationsDlg, id=ID_SCRIPT_LOCATIONS)
            self.Bind(wx.EVT_MENU, self.OnTitlesDlg, id=ID_SCRIPT_TITLES)
            self.Bind(
                wx.EVT_MENU,
                self.OnSpellCheckerScriptDictionaryDlg,
                id=ID_SCRIPT_SC_DICT,
            )
            self.Bind(wx.EVT_MENU, self.OnScriptSettings, id=ID_SCRIPT_SETTINGS_CHANGE)
            self.Bind(
                wx.EVT_MENU, self.OnLoadScriptSettings, id=ID_SCRIPT_SETTINGS_LOAD
            )
            self.Bind(
                wx.EVT_MENU, self.OnSaveScriptSettingsAs, id=ID_SCRIPT_SETTINGS_SAVE_AS
            )
            self.Bind(
                wx.EVT_MENU, self.OnReportDialogueChart, id=ID_REPORTS_DIALOGUE_CHART
            )
            self.Bind(wx.EVT_MENU, self.OnReportCharacter, id=ID_REPORTS_CHARACTER_REP)
            self.Bind(wx.EVT_MENU, self.OnReportScript, id=ID_REPORTS_SCRIPT_REP)
            self.Bind(wx.EVT_MENU, self.OnReportLocation, id=ID_REPORTS_LOCATION_REP)
            self.Bind(wx.EVT_MENU, self.OnReportScene, id=ID_REPORTS_SCENE_REP)
            self.Bind(wx.EVT_MENU, self.OnSpellCheckerDlg, id=ID_TOOLS_SPELL_CHECK)
            self.Bind(wx.EVT_MENU, self.OnNameDatabase, id=ID_TOOLS_NAME_DB)
            self.Bind(wx.EVT_MENU, self.OnCharacterMap, id=ID_TOOLS_CHARMAP)
            self.Bind(wx.EVT_MENU, self.OnCompareScripts, id=ID_TOOLS_COMPARE_SCRIPTS)
            self.Bind(wx.EVT_MENU, self.OnWatermark, id=ID_TOOLS_WATERMARK)
            self.Bind(wx.EVT_MENU, self.OnHelpCommands, id=ID_HELP_COMMANDS)
            self.Bind(wx.EVT_MENU, self.OnHelpManual, id=ID_HELP_MANUAL)
            self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_HELP_ABOUT)

        self.Bind(
            wx.EVT_MENU_RANGE,
            self.OnMRUFile,
            id=gd.mru.getIds()[0],
            id2=gd.mru.getIds()[1],
        )

        self.Bind(
            wx.EVT_MENU_RANGE,
            self.OnChangeType,
            id=ID_ELEM_TO_ACTION,
            id2=ID_ELEM_TO_TRANSITION,
        )

        def addTBMenu(id, menu):
            self.Bind(wx.EVT_MENU, partial(self.OnToolBarMenu, menu=menu), id=id)

        addTBMenu(ID_TOOLBAR_SETTINGS, settingsMenu)
        addTBMenu(ID_TOOLBAR_SCRIPTSETTINGS, scriptSettingsMenu)
        addTBMenu(ID_TOOLBAR_REPORTS, reportsMenu)
        addTBMenu(ID_TOOLBAR_VIEWS, viewMenu)
        addTBMenu(ID_TOOLBAR_TOOLS, toolsMenu)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)

        self.Layout()

    def init(self):
        self.updateKbdCommands()
        self.panel = self.createNewPanel()

    def mySetIcons(self):
        wx.Image.AddHandler(wx.PNGHandler())

        ib = wx.IconBundle()

        for sz in ("16", "32", "64", "128", "256"):
            ib.AddIcon(wx.Icon(misc.getBitmap("trelby/resources/icon%s.png" % sz)))

        self.SetIcons(ib)

    # def allocIds(self):

    #     g = globals()

    #     # see OnChangeType
    #     g["idToLTMap"] = {
    #         ID_ELEM_TO_SCENE: screenplay.SCENE,
    #         ID_ELEM_TO_ACTION: screenplay.ACTION,
    #         ID_ELEM_TO_CHARACTER: screenplay.CHARACTER,
    #         ID_ELEM_TO_DIALOGUE: screenplay.DIALOGUE,
    #         ID_ELEM_TO_PAREN: screenplay.PAREN,
    #         ID_ELEM_TO_TRANSITION: screenplay.TRANSITION,
    #         ID_ELEM_TO_SHOT: screenplay.SHOT,
    #         ID_ELEM_TO_ACTBREAK: screenplay.ACTBREAK,
    #         ID_ELEM_TO_NOTE: screenplay.NOTE,
    #     }

    def createNewPanel(self):
        newPanel = MyPanel(self.tabCtrl.getTabParent(), -1, self.gd)
        self.tabCtrl.addPage(newPanel, "")
        newPanel.ctrl.setTabText()
        newPanel.ctrl.SetFocus()

        return newPanel

    def setTitle(self, text):
        if self.film:
            self.SetTitle(
                "Trelby - %s - %s" % (_("film %s") % self.film.root.name, text)
            )
        else:
            self.SetTitle("Trelby - %s" % text)

    def setTabText(self, panel, text):
        i = self.findPage(panel)

        if i != -1:
            # strip out ".fountain" suffix from tab names (it's a bit
            # complicated since if we open the same file multiple times,
            # we have e.g. "foo.fountain" and "foo.fountain-2", so actually
            # we just strip out ".fountain" if it's found anywhere in the
            # string)

            s = text.replace(".fountain", "")
            self.tabCtrl.setTabText(i, s)

    # iterates over all tabs and finds out the corresponding page number
    # for the given panel.
    def findPage(self, panel):
        for i in range(self.tabCtrl.getPageCount()):
            p = self.tabCtrl.getPage(i)
            if p == panel:
                return i

        return -1

    # get list of MyCtrl objects for all open scripts
    def getCtrls(self):
        l = []

        for i in range(self.tabCtrl.getPageCount()):
            l.append(self.tabCtrl.getPage(i).ctrl)

        return l

    # returns True if any open script has been modified
    def isModifications(self):
        for c in self.getCtrls():
            if c.sp.isModified():
                return True

        return False

    def updateKbdCommands(self):
        self.gd.cfgGl.addShiftKeys()

        if self.gd.cfgGl.getConflictingKeys() != None:
            wx.MessageBox(
                _(
                    "You have at least one key bound to more than one\ncommand. The program will not work correctly until\nyou fix this."
                ),
                _("Warning"),
                wx.OK,
                self,
            )

        self.kbdCommands = {}

        for cmd in self.gd.cfgGl.commands:
            if not (cmd.isFixed and cmd.isMenu):
                for key in cmd.keys:
                    self.kbdCommands[key] = cmd

    # open script, in the current tab if it's untouched, or in a new one
    # otherwise
    def openScript(self, filename):
        if not self.tabCtrl.getPage(self.findPage(self.panel)).ctrl.isUntouched():
            self.panel = self.createNewPanel()

        self.panel.ctrl.loadFile(filename)
        self.panel.ctrl.updateScreen()
        self.gd.mru.add(filename)

    # select the tab holding filename, or open it like openScript; True if
    # it was opened now
    def showScript(self, filename):
        for i in range(self.tabCtrl.getPageCount()):
            if self.tabCtrl.getPage(i).ctrl.fileName == filename:
                self.tabCtrl.selectPage(i)

                return False

        self.openScript(filename)

        return True

    def checkFonts(self):
        names = ["Normal", "Bold", "Italic", "Bold-Italic"]
        failed = []

        for i, fi in enumerate(self.gd.cfgGui.fonts):
            if not util.isFixedWidth(fi.font):
                failed.append(names[i])

        if failed:
            wx.MessageBox(
                _(
                    "The fonts listed below are not fixed width and\nwill cause the program not to function correctly.\nPlease change the fonts at File/Settings/Change.\n\n\n"
                ).join(failed),
                _("Error"),
                wx.OK,
                self,
            )

    # If we get focus, pass it on to ctrl.
    def OnFocus(self, event):
        self.panel.ctrl.SetFocus()

    def OnMenuHighlight(self, event):
        # default implementation modifies status bar, so we need to
        # override it and do nothing
        pass

    def OnPageChange(self, page):
        self.panel = self.tabCtrl.getPage(page)
        self.showFilm(self.filmOf(self.panel.ctrl))
        self.panel.ctrl.SetFocus()
        self.panel.ctrl.updateCommon()
        self.setTitle(self.panel.ctrl.fileNameDisplay)

    def selectScript(self, toNext):
        current = self.tabCtrl.getSelectedPageIndex()
        pageCnt = self.tabCtrl.getPageCount()

        if toNext:
            pageNr = current + 1
        else:
            pageNr = current - 1

        if pageNr == -1:
            pageNr = pageCnt - 1
        elif pageNr == pageCnt:
            pageNr = 0

        if pageNr == current:
            # only one tab, nothing to do
            return

        self.tabCtrl.selectPage(pageNr)

    def OnScriptNext(self, event=None):
        self.selectScript(True)

    def OnScriptPrev(self, event=None):
        self.selectScript(False)

    def OnNewScript(self, event=None):
        self.panel = self.createNewPanel()

    def OnMRUFile(self, event):
        i = event.GetId() - self.gd.mru.getIds()[0]
        self.openScript(self.gd.mru.get(i))

    def OnOpen(self, event=None):
        dlg = wx.FileDialog(
            self,
            _("File to open"),
            misc.scriptDir,
            wildcard="Fountain (*.fountain)|*.fountain|" + _("All files") + "|*",
            style=wx.FD_OPEN,
        )

        if dlg.ShowModal() == wx.ID_OK:
            misc.scriptDir = dlg.GetDirectory()
            self.openScript(dlg.GetPath())

        dlg.Destroy()

    # pick a folder; None if the user cancelled
    def chooseFilmFolder(self, title):
        dlg = wx.DirDialog(self, title, misc.scriptDir)
        path = None

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            misc.scriptDir = os.path.dirname(path)

        dlg.Destroy()

        return path

    # f opened or made: kept with the open films (one from the same root
    # replaced) and shown with its bible when its script is the current tab
    def setFilm(self, f):
        self.openFilms.add(f)
        self.showFilm(self.filmOf(self.panel.ctrl))
        self.showBible(True)

    # the open film whose script ctrl holds, an openfilms.OpenFilm, or None
    def filmOf(self, ctrl):
        return self.openFilms.withScript(ctrl.fileName)

    # the current tab's film (an OpenFilm, or None for a script of no film)
    # becomes film, bible and annotations, in the bible panel and the title
    def showFilm(self, of):
        f, b = (of.film, of.bible) if of else (None, None)

        if f is self.film and b is self.bible:
            return

        self.film = f
        self.bible = b
        self.annotations = of.annotations if of else None
        self.biblePanel.setBible(b)
        self.setTitle(self.panel.ctrl.fileNameDisplay)

        for listener in self.filmListeners:
            listener()

    # a tab's file changed (open, Save As, a new script): the current tab's
    # film follows it
    def scriptFileChanged(self, ctrl):
        panel = getattr(self, "panel", None)

        if panel is not None and panel.ctrl is ctrl:
            self.showFilm(self.filmOf(ctrl))

    # File -> New film (file-format/layout/4): film.json in a folder with
    # none, and the current script saved as the film's script
    def OnNewFilm(self, event=None):
        root = self.chooseFilmFolder(_("Folder for the new film"))

        if root is None:
            return

        try:
            f = film.Film.create(root, "")
        except (film.FilmError, OSError) as e:
            wx.MessageBox(str(e), _("Error"), wx.OK, self)

            return

        ctrl = self.panel.ctrl

        if ctrl.saveFile(str(f.partPath("script"))):
            # the film was not open yet when the script was saved
            try:
                scriptsettings.saveFor(f, ctrl.sp)
            except Exception as e:
                wx.MessageBox(str(e), _("Error"), wx.OK, self)
        else:
            wx.MessageBox(
                _("The film was made, but the script was not saved into it."),
                _("New film"),
                wx.OK,
                self,
            )

        self.setFilm(f)

    # File -> Open film (file-format/layout/4): film.json, then its script
    # in a tab; what is missing or invalid is listed, the rest opens
    def OnOpenFilm(self, event=None):
        root = self.chooseFilmFolder(_("Film folder to open"))

        if root is not None:
            self.openFilm(root)

    def openFilm(self, root):
        try:
            f = film.Film.open(root)
        except film.FilmError as e:
            wx.MessageBox(
                _("This folder does not open as a film:") + "\n\n" + str(e),
                _("Open film"),
                wx.OK,
                self,
            )

            return

        script = f.partPath("script")

        if script.exists() and self.showScript(str(script)):
            self.loadFilmSettings(f)

        self.setFilm(f)
        self.listUnattached(f)

        if f.problems:
            dlg = relinkdlg.RelinkDlg(self, f.root, f.problems)
            dlg.ShowModal()
            dlg.Destroy()

            # the bible and the script may have been found in the dialog
            f.problems = []
            self.openFilms.at(f.root).reload()
            script = f.partPath("script")

            if script.exists() and self.showScript(str(script)):
                self.loadFilmSettings(f)

            self.showFilm(self.filmOf(self.panel.ctrl))

    # the film's settings record into its script's tab, just opened and the
    # current one (fountain-native/settings/1)
    def loadFilmSettings(self, f):
        ctrl = self.panel.ctrl

        if os.path.realpath(ctrl.fileName or "") == os.path.realpath(str(f.partPath("script"))):
            scriptsettings.loadFor(f, ctrl.sp)

            try:
                frontmatter.syncTitle(f, ctrl.sp)
            except Exception as e:
                f.problem(_("Front matter"), frontmatter.PATH, str(e))

            ctrl.sp.markChanged(False)
            ctrl.updateScreen()

    # the annotations whose text the opened script no longer has (edited in
    # another tool) are film problems, listed with the rest
    def listUnattached(self, f):
        ctrl = self.panel.ctrl

        if self.annotations is None or not self.isFilmScript(ctrl):
            return

        for rid, p in self.annotations.resolve(ctrl.sp, editing=False).items():
            if not p.attached:
                f.problem(_("Annotation %s") % rid, self.annotations.rel(rid), p.why)

    # whether ctrl holds an open film's script
    def isFilmScript(self, ctrl):
        return self.filmOf(ctrl) is not None

    # the annotations need the film's script in the current tab
    def annotationsReady(self):
        if self.annotations is None or not self.isFilmScript(self.panel.ctrl):
            wx.MessageBox(
                _("Annotations belong to a film's script: open the film (File -> Open film) and use its script's tab."),
                _("Annotations"),
                wx.OK,
                self,
            )

            return False

        return True

    def OnViewAnnotations(self, event=None):
        self.showAnnotations = self.menuBar.IsChecked(ID_VIEW_ANNOTATIONS)
        self.panel.ctrl.updateScreen()

    # Script -> Sync to spec (preprod-link/sync/2): the saved script's scene
    # index against the last accepted sync, shown in the change panel
    def OnSyncToSpec(self, event=None):
        ctrl = self.panel.ctrl
        of = self.filmOf(ctrl)

        if of is None:
            wx.MessageBox(
                _("Sync to spec works on a film's script: open the film (File -> Open film) and use its script's tab."),
                _("Sync to spec"),
                wx.OK,
                self,
            )

            return

        if ctrl.sp.isModified():
            if wx.MessageBox(
                _("The script has unsaved changes. Save it and sync?"),
                _("Sync to spec"),
                wx.YES_NO | wx.YES_DEFAULT,
                self,
            ) != wx.YES:
                return

            ctrl.OnSave()

            if ctrl.sp.isModified():
                return

        f, b = of.film, of.bible

        try:
            r = sync.run(f, b, ctrl.sp)
        except Exception as e:
            wx.MessageBox(str(e), _("Sync to spec"), wx.OK, self)

            return

        syncdlg.SyncDlg(self, f, b, r).Show()

    # Script -> Review proposals (preprod-link/review/1): the film's
    # proposals, TBDs and the values the latest sync lists as needs review
    def OnReview(self, event=None):
        if self.bible is None:
            wx.MessageBox(
                _("Proposals belong to a film: open the film (File -> Open film)."),
                _("Review proposals"),
                wx.OK,
                self,
            )

            return

        reviewdlg.ReviewDlg(self, self.bible, review.latestChanges(self.film)).Show()

    # Script -> Annotate: the selection's text, or the cursor's element
    def OnAnnotate(self, event=None):
        if not self.annotationsReady():
            return

        ctrl = self.panel.ctrl
        anchor = annotations.anchorAt(ctrl.sp)

        if anchor is None:
            wx.MessageBox(
                _("Put the cursor in a numbered scene (a new scene gets its number when the script is saved)."),
                _("Annotations"),
                wx.OK,
                self,
            )

            return

        scene, element, quote, occurrence = anchor
        where = _("Scene %s, element %d") % (scene, element) + (
            ": \"%s\"" % quote if quote else _(" (the whole element)")
        )
        dlg = annotationdlg.AnnotationDlg(self, None, where, self.bible)

        if dlg.ShowModal() == wx.ID_OK:
            try:
                values = dlg.values()
                a = self.annotations.add(
                    dlg.kindWord(), scene, element, quote, occurrence, dlg.text.GetValue().strip()
                )

                if values:
                    a.values.extend(values)
                    self.annotations.save(a, "creator")
            except Exception as e:
                wx.MessageBox(str(e), _("Annotations"), wx.OK, self)

        dlg.Destroy()
        ctrl.updateScreen()

    def editAnnotation(self, rid):
        a = self.annotations.records[rid]
        anc = a.anchor
        where = _("Scene %s") % anc.scene

        if anc.HasField("element"):
            where += _(", element %d") % anc.element

        if anc.HasField("quote"):
            where += ": \"%s\"" % anc.quote

        dlg = annotationdlg.AnnotationDlg(self, a, where, self.bible)

        if dlg.ShowModal() == wx.ID_OK:
            old = type(a)()
            old.CopyFrom(a)

            try:
                values = dlg.values()
                text = dlg.text.GetValue().strip()

                if text:
                    a.text = text
                else:
                    a.ClearField("text")

                del a.values[:]
                a.values.extend(values)
                self.annotations.save(a, "creator")
            except Exception as e:
                a.CopyFrom(old)
                wx.MessageBox(str(e), _("Annotations"), wx.OK, self)

        dlg.Destroy()

    # the list of annotations and what the creator does with one
    def annotationList(self, title, ids, canAttach):
        items = [(rid, self.annotations.describe(self.annotations.records[rid])) for rid in ids]

        if not items:
            wx.MessageBox(_("There are none."), title, wx.OK, self)

            return

        dlg = annotationdlg.AnnotationListDlg(self, title, items, canAttach)
        chosen = dlg.chosen if dlg.ShowModal() == wx.ID_OK else None
        dlg.Destroy()

        if chosen is None:
            return

        action, rid = chosen

        try:
            if action == "edit":
                self.editAnnotation(rid)
            elif action == "delete":
                if wx.MessageBox(
                    _("Delete this annotation?"), title, wx.YES_NO | wx.NO_DEFAULT, self
                ) == wx.YES:
                    self.annotations.delete(rid)
            elif action == "attach":
                anchor = annotations.anchorAt(self.panel.ctrl.sp)

                if anchor is None:
                    wx.MessageBox(_("Put the cursor in a numbered scene first."), title, wx.OK, self)
                else:
                    self.annotations.move(rid, *anchor)
        except Exception as e:
            wx.MessageBox(str(e), title, wx.OK, self)

        self.panel.ctrl.updateScreen()

    # Script -> Annotations here: on the cursor's text, element or scene
    def OnAnnotationsHere(self, event=None):
        if not self.annotationsReady():
            return

        sp = self.panel.ctrl.sp
        places = self.annotations.resolve(sp)
        anchor = annotations.anchorAt(sp)
        ids = []

        for rid, p in places.items():
            a = self.annotations.records[rid]
            onLine = any(l == sp.line for l, _c1, _c2 in p.spans)
            onScene = anchor and not p.spans and p.attached and a.anchor.scene == anchor[0]

            if onLine or onScene:
                ids.append(rid)

        self.annotationList(_("Annotations here"), ids, False)

    # Script -> Unattached annotations: those not found in the script, to
    # re-attach at the cursor or delete
    def OnAnnotationsUnattached(self, event=None):
        if not self.annotationsReady():
            return

        places = self.annotations.resolve(self.panel.ctrl.sp, editing=False)
        ids = [rid for rid, p in places.items() if not p.attached]
        self.annotationList(_("Unattached annotations"), ids, True)

    # show or hide the bible panel left of the scripts (View -> Bible)
    def showBible(self, show):
        if show and not self.splitter.IsSplit():
            self.biblePanel.Show()
            self.splitter.SplitVertically(
                self.biblePanel, self.scriptsPane, self.FromDIP(biblepanel.BiblePanel.WIDTH)
            )
        elif not show and self.splitter.IsSplit():
            self.splitter.Unsplit(self.biblePanel)

        self.menuBar.Check(ID_VIEW_BIBLE, show)

    def OnViewBible(self, event=None):
        self.showBible(self.menuBar.IsChecked(ID_VIEW_BIBLE))

    def OnSave(self, event=None):
        self.panel.ctrl.OnSave()

    def OnSaveScriptAs(self, event=None):
        self.panel.ctrl.OnSaveScriptAs()

    # the file to import, or None
    def askImportFile(self):
        dlg = wx.FileDialog(
            self,
            _("File to import"),
            misc.scriptDir,
            wildcard=_("Importable")
            + " "
            + _("files")
            + "(*.txt;*.fdx;*.celtx;*.astx;*.fountain;*.fadein;*.pdf)|"
            + "*.fdx;*.txt;*.celtx;*.astx;*.fountain;*.fadein;*.pdf|"
            + _("Formatted")
            + " "
            + _("text")
            + " "
            + _("files")
            + "(*.txt)|*.txt|"
            + "Final Draft XML(*.fdx)|*.fdx|"
            + "Celtx "
            + _("files")
            + " (*.celtx)|*.celtx|"
            + "Adobe Story XML "
            + _("files")
            + " (*.astx)|*.astx|"
            + "Fountain "
            + _("files")
            + " (*.fountain)|*.fountain|"
            + "Fadein "
            + _("files")
            + " (*.fadein)|*.fadein|"
            + "PDF "
            + _("files")
            + " (*.pdf)|*.pdf|"
            + _("All files")
            + "|*",
            style=wx.FD_OPEN,
        )

        path = None

        if dlg.ShowModal() == wx.ID_OK:
            misc.scriptDir = dlg.GetDirectory()
            path = dlg.GetPath()

        dlg.Destroy()

        return path

    # import path into a tab (a new one unless the current one is
    # untouched); returns its ctrl, or None when the import failed
    def importIntoTab(self, path):
        if not self.tabCtrl.getPage(self.findPage(self.panel)).ctrl.isUntouched():
            self.panel = self.createNewPanel()

        ok = self.panel.ctrl.importFile(path)
        self.panel.ctrl.updateScreen()

        return self.panel.ctrl if ok else None

    # File -> Import. with a film open (import-to-film, decision 3): into
    # this film, into a new folder (a new film), or just open it
    def OnImportScript(self, event=None):
        path = self.askImportFile()

        if path is None:
            return

        pick = None

        if self.film is not None:
            choices = [_("Into this film"), _("Into a new folder (a new film)"), _("Just open it")]
            dlg = wx.SingleChoiceDialog(
                self, _("Import %s:") % os.path.basename(path), _("Import"), choices
            )
            pick = dlg.GetSelection() if dlg.ShowModal() == wx.ID_OK else None
            dlg.Destroy()

            if pick is None:
                return

            if pick == 1:
                root = self.chooseFilmFolder(_("Folder for the new film"))

                if root is not None:
                    self.importIntoNewFilm(path, root)

                return

        ctrl = self.importIntoTab(path)

        if ctrl is not None and self.film is not None and pick == 0:
            # into this film: its bible gets the new items; this script's
            # scene numbers are not the film's, so no scene is linked
            biblereviewdlg.review(
                self, self.bible, ctrl.sp, True, False,
                _("Into this film's bible. The imported script is not the film's script, "
                  "so the new items are made without scenes."),
            )
            self.biblePanel.changed()

    # File -> Import into film (import-to-film/flow/1)
    def OnImportIntoFilm(self, event=None):
        path = self.askImportFile()

        if path is None:
            return

        root = self.chooseFilmFolder(_("Folder for the new film"))

        if root is not None:
            self.importIntoNewFilm(path, root)

    # import path, then make the film in root as New film does: the script
    # saved as its script.fountain (every scene numbered) and the original
    # copied into its source part. a failed or cancelled import makes no
    # film. returns the film, or None
    def importIntoNewFilm(self, path, root):
        if os.path.exists(os.path.join(root, "film.json")):
            wx.MessageBox(_("%s already holds a film.") % root, _("Import into film"), wx.OK, self)

            return None

        ctrl = self.importIntoTab(path)

        if ctrl is None:
            return None

        try:
            f = film.Film.create(root, "")
            importfilm.copySource(f, path)
        except (film.FilmError, film.OwnerError, OSError) as e:
            wx.MessageBox(str(e), _("Error"), wx.OK, self)

            return None

        # the imported title page goes into the film's front matter, and the
        # script is saved with the block written from it
        # (front-matter/import/1)
        try:
            frontmatter.syncTitle(f, ctrl.sp)
        except Exception as e:
            wx.MessageBox(str(e), _("Front matter"), wx.OK, self)

        if ctrl.saveFile(str(f.partPath("script"))):
            try:
                scriptsettings.saveFor(f, ctrl.sp)
            except Exception as e:
                wx.MessageBox(str(e), _("Error"), wx.OK, self)
        else:
            wx.MessageBox(
                _("The film was made, but the script was not saved into it."),
                _("Import into film"),
                wx.OK,
                self,
            )

        self.setFilm(f)
        self.reviewImport(ctrl)

        return f

    # the end of an import into a new film: the bible review, new items
    # ticked (import-to-film/flow/2, decision 1), then the report (flow/3)
    def reviewImport(self, ctrl):
        b = self.openFilms.at(self.film.root).bible if self.film else None

        if b is None:
            return

        made = biblereviewdlg.review(self, b, ctrl.sp, True)
        self.biblePanel.changed()
        dlg = importreportdlg.ImportReportDlg(
            self, ctrl, importfilm.report(b, ctrl.sp, made or {})
        )
        dlg.ShowModal()
        dlg.Destroy()

    def OnExportScript(self, event=None):
        self.panel.ctrl.OnExportScript()

    def OnCloseScript(self, event=None):
        if not self.panel.ctrl.canBeClosed():
            return

        if self.tabCtrl.getPageCount() > 1:
            self.tabCtrl.deletePage(self.tabCtrl.getSelectedPageIndex())
        else:
            self.panel.ctrl.createEmptySp()
            self.panel.ctrl.updateScreen()

    def OnRevertScript(self, event=None):
        self.panel.ctrl.OnRevertScript()

    def OnPrint(self, event=None):
        self.panel.ctrl.OnPrint()

    def OnSettings(self, event=None):
        self.panel.ctrl.OnSettings()

    def OnLoadSettings(self, event=None):
        dlg = wx.FileDialog(
            self,
            _("File to open"),
            defaultDir=os.path.dirname(self.gd.confFilename),
            defaultFile=os.path.basename(self.gd.confFilename),
            wildcard=_("Setting")
            + " "
            + _("files")
            + " (*.conf)|*.conf|"
            + _("All files")
            + "|*",
            style=wx.FD_OPEN,
        )

        if dlg.ShowModal() == wx.ID_OK:
            s = util.loadFile(dlg.GetPath(), self)

            if s:
                c = config.ConfigGlobal()
                c.load(s)
                self.gd.confFilename = dlg.GetPath()

                self.panel.ctrl.applyGlobalCfg(c, False)

        dlg.Destroy()

    def OnSaveSettingsAs(self, event=None):
        dlg = wx.FileDialog(
            self,
            _("Filename to save as"),
            defaultDir=os.path.dirname(self.gd.confFilename),
            defaultFile=os.path.basename(self.gd.confFilename),
            wildcard=_("Setting")
            + " "
            + _("files")
            + " (*.conf)|*.conf|"
            + _("All files")
            + "|*",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )

        if dlg.ShowModal() == wx.ID_OK:
            if util.writeToFile(dlg.GetPath(), self.gd.cfgGl.save(), self):
                self.gd.confFilename = dlg.GetPath()

        dlg.Destroy()

    def OnUndo(self, event=None):
        self.panel.ctrl.OnUndo()

    def OnRedo(self, event=None):
        self.panel.ctrl.OnRedo()

    def OnCut(self, event=None):
        self.panel.ctrl.OnCut()

    def OnCopy(self, event=None):
        self.panel.ctrl.OnCopy()

    def OnCopySystemCb(self, event=None):
        self.panel.ctrl.OnCopySystem(formatted=False)

    def OnCopySystemCbFormatted(self, event=None):
        self.panel.ctrl.OnCopySystem(formatted=True)

    def OnPaste(self, event=None):
        self.panel.ctrl.OnPaste()

    def OnPasteSystemCb(self, event=None):
        self.panel.ctrl.OnPasteSystemCb()

    def OnSelectScene(self, event=None):
        self.panel.ctrl.OnSelectScene()

    def OnSelectAll(self, event=None):
        self.panel.ctrl.OnSelectAll()

    def OnGotoPage(self, event=None):
        self.panel.ctrl.OnGotoPage()

    def OnGotoScene(self, event=None):
        self.panel.ctrl.OnGotoScene()

    def OnFindNextError(self, event=None):
        self.panel.ctrl.OnFindNextError()

    def OnFind(self, event=None):
        self.panel.ctrl.OnFind()

    def OnInsertNbsp(self, event=None):
        self.panel.ctrl.OnInsertNbsp()

    def OnDeleteElements(self, event=None):
        self.panel.ctrl.OnDeleteElements()

    def OnToggleShowFormatting(self, event=None):
        self.menuBar.Check(
            ID_VIEW_SHOW_FORMATTING, not self.menuBar.IsChecked(ID_VIEW_SHOW_FORMATTING)
        )
        self.showFormatting = not self.showFormatting
        self.panel.ctrl.Refresh(False)

    def OnShowFormatting(self, event=None):
        self.showFormatting = self.menuBar.IsChecked(ID_VIEW_SHOW_FORMATTING)
        self.panel.ctrl.Refresh(False)

    def OnDarkTheme(self, event=None):
        self.panel.ctrl.OnDarkTheme(self.menuBar.IsChecked(ID_VIEW_DARK_THEME))

    # make View -> Dark theme show the current theme.
    def updateThemeMenu(self):
        self.menuBar.Check(
            ID_VIEW_DARK_THEME, self.gd.cfgGl.theme == config.THEME_DARK
        )

    def OnViewModeDraft(self):
        self.menuBar.Check(ID_VIEW_STYLE_DRAFT, True)
        self.OnViewModeChange()

    def ShowHideToolbar(self, event=None):
        self.CheckToolbar = self.menuBar.IsChecked(ID_SHOW_HIDE_TOOLBAR)

        if self.CheckToolbar == True:
            self.toolBar.Hide()

        else:
            self.toolBar.Show()

    def OnViewModeLayout(self):
        self.menuBar.Check(ID_VIEW_STYLE_LAYOUT, True)
        self.OnViewModeChange()

    def OnViewModeSideBySide(self):
        self.menuBar.Check(ID_VIEW_STYLE_SIDE_BY_SIDE, True)
        self.OnViewModeChange()

    def OnViewModeChange(self, event=None):
        if self.menuBar.IsChecked(ID_VIEW_STYLE_DRAFT):
            mode = self.gd.VIEWMODE_DRAFT
        elif self.menuBar.IsChecked(ID_VIEW_STYLE_LAYOUT):
            mode = self.gd.VIEWMODE_LAYOUT
        else:
            mode = self.gd.VIEWMODE_SIDE_BY_SIDE

        self.gd.setViewMode(mode)

        for c in self.getCtrls():
            c.refreshCache()

        c = self.panel.ctrl
        c.makeLineVisible(c.sp.line)
        c.updateScreen()

    # clicking the status area (its zoom control) gives it the keyboard
    # focus; we never want that, pass it on to the current script
    def OnStatusFocus(self, event):
        self.panel.ctrl.SetFocus()

    def OnZoomIn(self, event=None):
        self.panel.ctrl.OnZoomIn()

    def OnZoomOut(self, event=None):
        self.panel.ctrl.OnZoomOut()

    def OnZoomReset(self, event=None):
        self.panel.ctrl.OnZoomReset()

    def ToggleFullscreen(self, event=None):
        self.noFSBtn.Show(not self.IsFullScreen())
        self.ShowFullScreen(not self.IsFullScreen(), wx.FULLSCREEN_ALL)
        self.panel.ctrl.SetFocus()

    def OnPaginate(self, event=None):
        self.panel.ctrl.OnPaginate()

    def OnRenumberScenes(self, event=None):
        self.panel.ctrl.OnRenumberScenes()

    def OnAutoCompletionDlg(self, event=None):
        self.panel.ctrl.OnAutoCompletionDlg()

    def OnTitlesDlg(self, event=None):
        self.panel.ctrl.OnTitlesDlg()

    def OnHeadersDlg(self, event=None):
        self.panel.ctrl.OnHeadersDlg()

    def OnLocationsDlg(self, event=None):
        self.panel.ctrl.OnLocationsDlg()

    def OnSpellCheckerDictionaryDlg(self, event=None):
        dlg = spellcheckcfgdlg.SCDictDlg(self, copy.deepcopy(self.gd.scDict), True)

        if dlg.ShowModal() == wx.ID_OK:
            self.gd.scDict = dlg.scDict
            self.gd.saveScDict()

        dlg.Destroy()

    def OnSpellCheckerScriptDictionaryDlg(self, event=None):
        self.panel.ctrl.OnSpellCheckerScriptDictionaryDlg()

    def OnWatermark(self, event=None):
        self.panel.ctrl.OnWatermark()

    def OnScriptSettings(self, event=None):
        self.panel.ctrl.OnScriptSettings()

    def OnLoadScriptSettings(self, event=None):
        dlg = wx.FileDialog(
            self,
            _("File to open"),
            defaultDir=self.gd.scriptSettingsPath,
            wildcard=_("Script")
            + " "
            + _("setting")
            + " "
            + _("files")
            + " (*.sconf)|*.sconf|"
            + _("All files")
            + "|*",
            style=wx.FD_OPEN,
        )

        if dlg.ShowModal() == wx.ID_OK:
            s = util.loadFile(dlg.GetPath(), self)

            if s:
                cfg = config.Config()
                cfg.load(s)
                self.panel.ctrl.applyCfg(cfg)

                self.gd.scriptSettingsPath = os.path.dirname(dlg.GetPath())

        dlg.Destroy()

    def OnSaveScriptSettingsAs(self, event=None):
        dlg = wx.FileDialog(
            self,
            _("Filename to save as"),
            defaultDir=self.gd.scriptSettingsPath,
            wildcard=_("Script")
            + " "
            + _("setting")
            + _("files")
            + " (*.sconf)|*.sconf|"
            + _("All files")
            + "|*",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )

        if dlg.ShowModal() == wx.ID_OK:
            if util.writeToFile(dlg.GetPath(), self.panel.ctrl.sp.saveCfg(), self):
                self.gd.scriptSettingsPath = os.path.dirname(dlg.GetPath())

        dlg.Destroy()

    def OnReportCharacter(self, event=None):
        self.panel.ctrl.OnReportCharacter()

    def OnReportDialogueChart(self, event=None):
        self.panel.ctrl.OnReportDialogueChart()

    def OnReportLocation(self, event=None):
        self.panel.ctrl.OnReportLocation()

    def OnReportScene(self, event=None):
        self.panel.ctrl.OnReportScene()

    def OnReportScript(self, event=None):
        self.panel.ctrl.OnReportScript()

    def OnSpellCheckerDlg(self, event=None):
        self.panel.ctrl.OnSpellCheckerDlg()

    def OnNameDatabase(self, event=None):
        if not namesdlg.readNames(self):
            wx.MessageBox(_("Error opening name database."), _("Error"), wx.OK, self)

            return

        dlg = namesdlg.NamesDlg(self, self.panel.ctrl)
        dlg.ShowModal()
        dlg.Destroy()

    def OnCharacterMap(self, event=None):
        dlg = charmapdlg.CharMapDlg(self, self.panel.ctrl)
        dlg.ShowModal()
        dlg.Destroy()

    def OnCompareScripts(self, event=None):
        self.panel.ctrl.OnCompareScripts()

    def OnChangeType(self, event):
        self.panel.ctrl.OnChangeType(event)

    def OnHelpCommands(self, event=None):
        dlg = commandsdlg.CommandsDlg(self.gd.cfgGl)
        dlg.Show()

    def OnHelpManual(self, event=None):
        manual.show(self)

    def OnAbout(self, event=None):
        win = splash.SplashWindow(self, -1)
        win.Show()

    def OnToolBarMenu(self, event, menu):
        self.PopupMenu(menu)

    # saves every modified script, showing its tab first so a Save As
    # dialog says which script it is for. returns False as soon as one is
    # still unsaved (Save As cancelled, or a write error), so the exit can
    # be called off instead of losing it.
    def saveAll(self):
        for i in range(self.tabCtrl.getPageCount()):
            ctrl = self.tabCtrl.getPage(i).ctrl

            if ctrl.sp.isModified():
                self.tabCtrl.selectPage(i)
                ctrl.OnSave()

                if ctrl.sp.isModified():
                    return False

        return True

    def OnCloseWindow(self, event):
        doExit = True
        if event.CanVeto() and self.isModifications():
            close_msg_box = wx.MessageDialog(
                self,
                _("You have unsaved changes. Do\nyou want to save your changes?"),
                _("Save Changes"),
                wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT,
            )
            close_msg_box.SetYesNoLabels(wx.ID_SAVE, "(&D) " + _("Don't save"))
            response = close_msg_box.ShowModal()
            if response == wx.ID_YES:
                doExit = self.saveAll()
            elif response == wx.ID_CANCEL:
                doExit = False

        if doExit:
            util.writeToFile(self.gd.stateFilename, self.gd.save(), self)
            util.removeTempFiles(misc.tmpPrefix)
            self.Destroy()
            self.myApp.ExitMainLoop()
        else:
            event.Veto()

    def OnExit(self, event):
        self.Close(False)

    def OnMove(self, event):
        self.gd.posX, self.gd.posY = self.GetPosition()
        event.Skip()

    def OnSize(self, event):
        self.gd.width, self.gd.height = self.GetSize()
        event.Skip()

    def getCfgGui(self):
        return self.gd.cfgGui
