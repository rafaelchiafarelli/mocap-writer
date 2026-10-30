# a script's settings as a film record (fountain-native/settings/1): page
# setup, element styles, PDF options, strings, headers, auto-completion,
# locations, the script's spelling words and the title page layout, kept in
# the film's `settings` part as a mocap-contracts ScriptSettings. a
# .fountain has no place for them, so a script opened outside a film opens
# with defaults, as before. no wx.
#
# every field is written, defaults included; a value outside Trelby's
# limits is refused by the contract, not clamped, and the script then opens
# with defaults and the problem is listed.

import mocap_contracts as mc

import trelby.config as config
import trelby.headers as headers
import trelby.pml as pml
import trelby.screenplay as screenplay
import trelby.titles as titles
import trelby.util as util

# line type <-> ScriptElement name
ELEMENTS = (
    (screenplay.SCENE, "SCENE"),
    (screenplay.ACTION, "ACTION"),
    (screenplay.CHARACTER, "CHARACTER"),
    (screenplay.DIALOGUE, "DIALOGUE"),
    (screenplay.PAREN, "PAREN"),
    (screenplay.TRANSITION, "TRANSITION"),
    (screenplay.SHOT, "SHOT"),
    (screenplay.ACTBREAK, "ACT_BREAK"),
    (screenplay.NOTE, "NOTE"),
)

# Config attribute <-> PageSettings field
PAGE = (
    ("paperWidth", "paper_width_mm"),
    ("paperHeight", "paper_height_mm"),
    ("marginTop", "margin_top_mm"),
    ("marginBottom", "margin_bottom_mm"),
    ("marginLeft", "margin_left_mm"),
    ("marginRight", "margin_right_mm"),
    ("fontSize", "font_size_pt"),
    ("pbActionLines", "page_break_action_lines"),
    ("pbDialogueLines", "page_break_dialogue_lines"),
    ("sceneContinueds", "scene_continueds"),
    ("sceneContinuedIndent", "scene_continued_indent_chars"),
)

PDF = (
    ("pdfShowSceneNumbers", "show_scene_numbers"),
    ("pdfIncludeTOC", "include_toc"),
    ("pdfShowTOC", "show_toc"),
    ("pdfOpenOnCurrentPage", "open_on_current_page"),
    ("pdfRemoveNotes", "remove_notes"),
    ("pdfOutlineNotes", "outline_notes"),
    ("pdfShowMargins", "show_margins"),
    ("pdfShowLineNumbers", "show_line_numbers"),
)

FONTS = (
    (config.PDF_FONT_NORMAL, "normal"),
    (config.PDF_FONT_BOLD, "bold"),
    (config.PDF_FONT_ITALIC, "italic"),
    (config.PDF_FONT_BOLD_ITALIC, "bold_italic"),
)

STRINGS = (
    ("strMore", "more"),
    ("strContinuedPageEnd", "continued_page_end"),
    ("strContinuedPageStart", "continued_page_start"),
    ("strDialogueContinued", "dialogue_continued"),
)

STYLE = (
    ("isCaps", "caps"),
    ("isBold", "bold"),
    ("isItalic", "italic"),
    ("isUnderlined", "underlined"),
)

ALIGNS = (
    (util.ALIGN_LEFT, "TEXT_ALIGN_LEFT"),
    (util.ALIGN_CENTER, "TEXT_ALIGN_CENTER"),
    (util.ALIGN_RIGHT, "TEXT_ALIGN_RIGHT"),
)

TITLE_FONTS = (
    (pml.COURIER, "TITLE_FONT_COURIER"),
    (pml.HELVETICA, "TITLE_FONT_HELVETICA"),
    (pml.TIMES_ROMAN, "TITLE_FONT_TIMES"),
)


def _flag(b):
    return mc.Flag.Value("FLAG_ON" if b else "FLAG_OFF")


def _bool(f):
    return f == mc.Flag.Value("FLAG_ON")


def _elem(lt):
    return mc.ScriptElement.Value("SCRIPT_ELEMENT_" + dict(ELEMENTS)[lt])


def _lt(value):
    name = mc.ScriptElement.Name(value).removeprefix("SCRIPT_ELEMENT_")

    return {n: lt for lt, n in ELEMENTS}[name]


# the record of sp's settings. fountainTitle is the Fountain title block
# the script was saved with (sp.fountainSource.title)
def toRecord(sp, fountainTitle=""):
    cfg = sp.cfg
    s = mc.ScriptSettings()

    for attr, field in PAGE:
        v = getattr(cfg, attr)
        setattr(s.page, field, _flag(v) if isinstance(v, bool) else v)

    for lt, _n in ELEMENTS:
        t = cfg.getType(lt)
        e = s.elements.add(
            element=_elem(lt),
            before_spacing_tenths=t.beforeSpacing,
            intra_spacing_tenths=t.intraSpacing,
            indent_chars=t.indent,
            width_chars=t.width,
        )

        for side in ("screen", "export"):
            for attr, field in STYLE:
                setattr(getattr(e, side), field, _flag(getattr(getattr(t, side), attr)))

    for attr, field in PDF:
        setattr(s.pdf, field, _flag(getattr(cfg, attr)))

    for name, field in FONTS:
        fi = cfg.getPDFFont(name)
        f = getattr(s.pdf, field)
        f.pdf_name = fi.pdfName
        f.filename = fi.filename

    for attr, field in STRINGS:
        setattr(s.strings, field, getattr(cfg, attr))

    s.headers.empty_lines_after = sp.headers.emptyLinesAfter

    for h in sp.headers.hdrs:
        s.headers.lines.add(
            line=h.line,
            x_offset_chars=h.xoff,
            align=mc.TextAlign.Value(dict(ALIGNS)[h.align]),
            bold=_flag(h.isBold),
            italic=_flag(h.isItalic),
            underlined=_flag(h.isUnderlined),
            text=h.text,
        )

    for lt, t in sp.autoCompletion.types.items():
        s.auto_completion.add(element=_elem(lt), enabled=_flag(t.enabled), items=list(t.items))

    for group in sp.locations.locations:
        s.locations.add(headings=list(group))

    s.spelling_words.extend(sorted(sp.scDict.words))

    for pg in sp.titles.pages:
        page = s.title_page.pages.add()

        for ts in pg:
            align = (
                util.ALIGN_CENTER
                if ts.isCentered
                else util.ALIGN_RIGHT
                if ts.isRightJustified
                else util.ALIGN_LEFT
            )
            page.strings.add(
                items=list(ts.items),
                x_mm=ts.x,
                y_mm=ts.y,
                size_pt=ts.size,
                align=mc.TextAlign.Value(dict(ALIGNS)[align]),
                bold=_flag(ts.isBold),
                italic=_flag(ts.isItalic),
                underlined=_flag(ts.isUnderlined),
                font=mc.TitleFont.Value(dict(TITLE_FONTS).get(ts.font, "TITLE_FONT_COURIER")),
            )

    s.title_page.fountain_title = fountainTitle

    return s


# put the record's settings into sp. the title pages' layout is used only
# while the script's title block (fountainTitle) is still the one the
# layout was saved with; returns a list of problems as text (the title
# page edited elsewhere).
def apply(sp, s, fountainTitle):
    problems = []
    cfg = sp.cfg

    for attr, field in PAGE:
        v = getattr(s.page, field)
        setattr(cfg, attr, _bool(v) if isinstance(getattr(cfg, attr), bool) else v)

    for e in s.elements:
        t = cfg.getType(_lt(e.element))
        t.beforeSpacing = e.before_spacing_tenths
        t.intraSpacing = e.intra_spacing_tenths
        t.indent = e.indent_chars
        t.width = e.width_chars

        for side in ("screen", "export"):
            for attr, field in STYLE:
                setattr(getattr(t, side), attr, _bool(getattr(getattr(e, side), field)))

    for attr, field in PDF:
        setattr(cfg, attr, _bool(getattr(s.pdf, field)))

    for name, field in FONTS:
        fi = cfg.getPDFFont(name)
        f = getattr(s.pdf, field)
        fi.pdfName = f.pdf_name
        fi.filename = f.filename

    for attr, field in STRINGS:
        setattr(cfg, attr, getattr(s.strings, field))

    cfg.recalc()

    sp.headers = headers.Headers()
    sp.headers.emptyLinesAfter = s.headers.empty_lines_after
    aligns = {n: a for a, n in ALIGNS}

    for h in s.headers.lines:
        hs = headers.HeaderString()
        hs.line = h.line
        hs.xoff = h.x_offset_chars
        hs.align = aligns[mc.TextAlign.Name(h.align)]
        hs.isBold = _bool(h.bold)
        hs.isItalic = _bool(h.italic)
        hs.isUnderlined = _bool(h.underlined)
        hs.text = h.text
        sp.headers.hdrs.append(hs)

    for a in s.auto_completion:
        t = sp.autoCompletion.types.get(_lt(a.element))

        if t is not None:
            t.enabled = _bool(a.enabled)
            t.items = list(a.items)

    sp.locations.locations = [list(g.headings) for g in s.locations]
    sp.scDict.words = {w: None for w in s.spelling_words}

    if s.title_page.pages:
        if s.title_page.fountain_title == fountainTitle:
            fonts = {n: f for f, n in TITLE_FONTS}
            tt = titles.Titles()

            for page in s.title_page.pages:
                pg = []

                for ts in page.strings:
                    t = titles.TitleString(
                        list(ts.items),
                        ts.x_mm,
                        ts.y_mm,
                        mc.TextAlign.Name(ts.align) == "TEXT_ALIGN_CENTER",
                        _bool(ts.bold),
                        ts.size_pt,
                        fonts[mc.TitleFont.Name(ts.font)],
                    )
                    t.isRightJustified = mc.TextAlign.Name(ts.align) == "TEXT_ALIGN_RIGHT"
                    t.isItalic = _bool(ts.italic)
                    t.isUnderlined = _bool(ts.underlined)
                    pg.append(t)

                tt.pages.append(pg)

            sp.titles = tt
        else:
            problems.append(
                _(
                    "The title page was edited outside the writer: it opens "
                    "from the Fountain text in the default layout."
                )
            )

    sp.reformatAll()
    sp.paginate()

    return problems


# the settings record's text for sp
def toJson(sp, fountainTitle=""):
    return mc.to_json(toRecord(sp, fountainTitle))


def fromJson(text):
    return mc.from_json(mc.ScriptSettings, text)


# the film's settings path for its script, or None if the film has no
# settings part
def _rel(film):
    p = film.part("settings")

    return p.path if p and not p.path.endswith("/") else None


# write sp's settings into film, after the script was saved there. the
# change log records them (a record of the settings part).
def saveFor(film, sp):
    rel = _rel(film)

    if rel is None:
        return

    title = sp.fountainSource.title if sp.fountainSource else ""
    film.writeText(rel, toJson(sp, title))


# put film's settings into sp, the script just opened from it; what is
# invalid is a film problem, and sp keeps the defaults
def loadFor(film, sp):
    rel = _rel(film)

    if rel is None or not (film.root / rel).is_file():
        return

    try:
        s = fromJson(film.readText(rel))
    except mc.ContractError as e:
        film.problem(_("Script settings"), rel, str(e) + " " + _("(the script uses the defaults)"))

        return

    title = sp.fountainSource.title if sp.fountainSource else ""

    for why in apply(sp, s, title):
        film.problem(_("Script settings"), rel, why)
