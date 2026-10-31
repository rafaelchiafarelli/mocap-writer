import wx

import trelby.importfilm as importfilm


# the import report (import-to-film/flow/3): what was made and what still
# needs the creator, as text the creator can save; Go to the first IMPORT:
# note puts the cursor on it.
class ImportReportDlg(wx.Dialog):
    def __init__(self, frame, ctrl, text):
        wx.Dialog.__init__(
            self, frame, -1, _("Import report"), size=frame.FromDIP(wx.Size(560, 460)),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.ctrl = ctrl
        self.text = text
        vsizer = wx.BoxSizer(wx.VERTICAL)
        tc = wx.TextCtrl(self, -1, text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vsizer.Add(tc, 1, wx.EXPAND | wx.ALL, 8)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.notes = importfilm.importNotes(ctrl.sp)
        gotoBtn = wx.Button(self, -1, _("Go to the first IMPORT: note"))
        gotoBtn.Enable(bool(self.notes))
        gotoBtn.Bind(wx.EVT_BUTTON, self.OnGoto)
        saveBtn = wx.Button(self, -1, _("Save..."))
        saveBtn.Bind(wx.EVT_BUTTON, self.OnSave)
        okBtn = wx.Button(self, wx.ID_OK)

        for b in (gotoBtn, saveBtn, okBtn):
            hsizer.Add(b, 0, wx.RIGHT, 6)

        vsizer.Add(hsizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8)
        self.SetSizer(vsizer)

    def OnGoto(self, event=None):
        line = self.notes[0]
        self.ctrl.sp.line = line
        self.ctrl.sp.column = 0
        self.ctrl.makeLineVisible(line)
        self.ctrl.updateScreen()
        self.EndModal(wx.ID_OK)

    def OnSave(self, event=None):
        dlg = wx.FileDialog(
            self, _("Save the report as"), wildcard=_("Text files") + " (*.txt)|*.txt",
            defaultFile="import-report.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        )

        if dlg.ShowModal() == wx.ID_OK:
            try:
                with open(dlg.GetPath(), "w", encoding="utf-8") as fp:
                    fp.write(self.text)
            except OSError as e:
                wx.MessageBox(str(e), _("Error"), wx.OK, self)

        dlg.Destroy()
