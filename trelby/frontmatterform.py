import wx

import trelby.frontmatter as frontmatter

# (page, include flag or None, [(key, label, multi-line)]) in the form's
# order; key is "<message>.<field>" of the FrontMatter
PAGES = (
    ("Title page", None, [
        ("title.title", "Title", False), ("title.subtitle", "Subtitle", False),
        ("title.episode", "Episode", False), ("title.author", "Author", False),
        ("title.co_authors", "Co-authors (one per line)", True),
        ("title.email", "E-mail", False),
    ]),
    ("Overview", "overview.include", [
        ("overview.cast", "Cast (from the bible's characters)", None),
        ("overview.sets", "Sets (from the bible's sets)", None),
        ("overview.acts", "Act breakdown (pages and scenes)", None),
    ]),
    ("Pitch", "pitch.include", [
        ("pitch.pitch", "Pitch", True), ("pitch.logline", "Logline", True),
        ("pitch.target_audience", "Target audience", False),
    ]),
    ("Argument", "argument.include", [("argument.text", "Argument", True)]),
)


def _get(fm, key):
    msg, field = key.split(".")

    return getattr(getattr(fm, msg), field)


def _set(fm, key, value):
    msg, field = key.split(".")
    m = getattr(fm, msg)

    if field == "co_authors":
        del m.co_authors[:]
        m.co_authors.extend(value)
    else:
        setattr(m, field, value)


# the front matter's form under the bible tree (front-matter/record/1): the
# title page's fields, then each optional page with its Include tick; a
# text is saved when it loses the focus, a tick at once
class FrontMatterForm(wx.ScrolledWindow):
    def __init__(self, parent, id, panel):
        wx.ScrolledWindow.__init__(self, parent, id, style=wx.VSCROLL)
        self.SetScrollRate(0, 10)
        self.panel = panel
        self.film = None
        self.fm = None

        # key -> control
        self.ctrls = {}
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))

    def setFilm(self, film):
        self.commitFocused()
        self.film = film
        self.fm = frontmatter.load(film) if film else None
        self.build()

    def build(self):
        self.DestroyChildren()
        self.ctrls = {}
        sizer = self.GetSizer()
        sizer.Clear()

        if self.fm is None:
            return

        title = wx.StaticText(self, -1, _("Front matter"))
        title.SetFont(title.GetFont().Bold().Larger())
        sizer.Add(title, 0, wx.ALL, 6)

        for page, include, fields in PAGES:
            head = wx.StaticText(self, -1, _(page))
            head.SetFont(head.GetFont().Bold())
            sizer.Add(head, 0, wx.LEFT | wx.TOP, 6)

            if include:
                cb = wx.CheckBox(self, -1, _("Include this page"))
                cb.SetValue(frontmatter.isOn(_get(self.fm, include)))
                cb.Bind(wx.EVT_CHECKBOX, lambda e, k=include: self.OnFlag(k))
                sizer.Add(cb, 0, wx.LEFT | wx.TOP, 6)
                self.ctrls[include] = cb

            for key, label, multi in fields:
                if multi is None:
                    cb = wx.CheckBox(self, -1, _(label))
                    cb.SetValue(frontmatter.isOn(_get(self.fm, key)))
                    cb.Bind(wx.EVT_CHECKBOX, lambda e, k=key: self.OnFlag(k))
                    sizer.Add(cb, 0, wx.LEFT | wx.TOP, 12)
                    self.ctrls[key] = cb

                    continue

                sizer.Add(wx.StaticText(self, -1, _(label)), 0, wx.LEFT | wx.TOP, 6)
                value = _get(self.fm, key)
                text = "\n".join(value) if key == "title.co_authors" else value
                style = wx.TE_MULTILINE if multi else wx.TE_PROCESS_ENTER
                tc = wx.TextCtrl(self, -1, text, style=style)

                if multi:
                    tc.SetMinSize(wx.Size(-1, self.FromDIP(160 if key == "argument.text" else 60)))

                tc.Bind(wx.EVT_KILL_FOCUS, lambda e, k=key: (self.OnText(k), e.Skip()))
                if not multi:
                    tc.Bind(wx.EVT_TEXT_ENTER, lambda e, k=key: self.OnText(k))
                sizer.Add(tc, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
                self.ctrls[key] = tc

        self.FitInside()
        self.Layout()

    def save(self):
        try:
            frontmatter.save(self.film, self.fm)
        except Exception as e:
            wx.MessageBox(str(e), _("Front matter"), wx.OK, self)
            self.fm = frontmatter.load(self.film)
            wx.CallAfter(self.build)

    def OnText(self, key):
        if self.fm is None or key not in self.ctrls:
            return

        v = self.ctrls[key].GetValue()

        if key == "title.co_authors":
            v = [x.strip() for x in v.splitlines() if x.strip()]

        if v != (list(_get(self.fm, key)) if key == "title.co_authors" else _get(self.fm, key)):
            _set(self.fm, key, v)
            self.save()

    def OnFlag(self, key):
        _set(self.fm, key, frontmatter.ON if self.ctrls[key].GetValue() else frontmatter.OFF)
        self.save()

    # save the text being typed in, if any
    def commitFocused(self):
        focus = wx.Window.FindFocus()

        for key, ctrl in self.ctrls.items():
            if ctrl is focus and isinstance(ctrl, wx.TextCtrl):
                self.OnText(key)
