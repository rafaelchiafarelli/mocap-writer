import os
import re
from unittest import mock

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import tests.u as u
import trelby.fountain as fountain
import trelby.pdfimport as pdfimport
import trelby.screenplay as screenplay
import trelby.translations as translations

_ = translations.trelby_translations_load()

PROFILE = u.fixtureFilePath("pdf/letter-test.toml")
TRELBY_PROFILE = os.path.join(
    os.path.dirname(pdfimport.__file__), "pdfprofiles", "trelby-a4.toml"
)

CW = 7.2  # Courier 12 character width, points


# draw a PDF of pages; each page a list of (x, top, text), top = distance
# from the top of the page to the top of the line. A text ending in ">" is
# right-aligned at x (x is then its right edge).
def makePdf(path, pages):
    c = canvas.Canvas(str(path), pagesize=letter)
    h = letter[1]
    for page in pages:
        c.setFont("Courier", 12)
        for x, top, text in page:
            # pdfplumber's "top" is the top of the glyph box: baseline - ascent
            y = h - top - 12 * 0.629
            if text.endswith(">"):
                text = text[:-1]
                c.drawString(x - len(text) * CW, y, text)
            else:
                c.drawString(x, y, text)
        c.showPage()
    c.save()
    return str(path)


# lines at 12 pt steps starting at top 72; None = blank line
def page(*rows):
    out = []
    top = 72.0
    for r in rows:
        if r is not None:
            x, text = r
            out.append((x, top, text))
        top += 12.0
    return out


A, D, P, C = 108.0, 180.0, 216.0, 252.0


def fountainOf(lines):
    return fountain.generate(pdfimport.toScreenplay(lines)).text


# import with the test profile; no IMPORT: notes unless asked
def importPages(tmp_path, pages, **kw):
    path = makePdf(tmp_path / "t.pdf", pages)
    kw.setdefault("notes", False)
    return pdfimport.importPdf(path, pdfimport.loadProfile(PROFILE), **kw)


# import with the layout detected from the PDF (what File > Import does)
def detectPages(tmp_path, pages, **kw):
    path = makePdf(tmp_path / "t.pdf", pages)
    return pdfimport.importPdf(path, None, **kw)


def testBasicFountain(tmp_path):
    pages = [
        page(
            (A, "EXT. PRAÇA - DIA"),
            None,
            (A, "Uma praça vazia. O vento"),
            (A, "levanta folhas secas."),
            None,
            (C, "JOÃO"),
            (P, "(baixo)"),
            (D, "Ninguém veio."),
            None,
            (C, "CONCEIÇÃO"),
            (D, "Ainda é cedo."),
            None,
            (540.0, "CORTA PARA:>"),
        )
    ]
    lines = importPages(tmp_path, pages)

    assert fountainOf(lines) == (
        "EXT. PRAÇA - DIA\n"
        "\n"
        "Uma praça vazia. O vento levanta folhas secas.\n"
        "\n"
        "JOÃO\n"
        "(baixo)\n"
        "Ninguém veio.\n"
        "\n"
        "CONCEIÇÃO\n"
        "Ainda é cedo.\n"
        "\n"
        "> CORTA PARA:\n"
    )


# the Fountain a PDF import writes reads back to the same elements
# (fountain-native/io/5: the import writes with fountain.generate)
def testFountainReadsBack(tmp_path):
    pages = [
        page(
            (A, "INT. CASA - NOITE"),
            None,
            (A, "EXTRA chega. INTO the dark."),
            None,
            (C, "BETO"),
            (P, "(baixo)"),
            (D, "Mudou sim."),
            None,
            (540.0, "CORTA PARA:>"),
        )
    ]
    sp = pdfimport.toScreenplay(importPages(tmp_path, pages))
    back = fountain.load(fountain.generate(sp).text, sp.cfgGl)

    assert fountain.elementsOf(back) == fountain.elementsOf(sp)


def testElementLinesMeetImporterContract(tmp_path):
    lines = importPages(tmp_path, [page((A, "INT. CASA - NOITE"), None, (A, "Escuro."))])

    assert [(ln.lb, ln.lt, ln.text) for ln in lines] == [
        (screenplay.LB_LAST, screenplay.SCENE, "INT. CASA - NOITE"),
        (screenplay.LB_LAST, screenplay.ACTION, "Escuro."),
    ]

    sp = pdfimport.toScreenplay(lines)
    sp._validate()


def testUnknownIndentStopsWithPageAndLine(tmp_path):
    pages = [
        page((A, "INT. CASA - NOITE")),
        page((A, "Escuro."), None, (300.0, "PERDIDO")),
    ]
    with pytest.raises(pdfimport.PdfImportError) as ei:
        importPages(tmp_path, pages, strict=True)

    assert ei.value.page == 2
    assert ei.value.lineNo == 2
    assert "page 2, line 2" in str(ei.value)
    assert "PERDIDO" in str(ei.value)


def testPageFurnitureDropped(tmp_path):
    pages = [
        page((A, "INT. CASA - NOITE"), None, (C, "ANA"), (D, "Primeira fala."), None, (A, "Ela sai.")),
        [(510.0, 36.0, "2.")]
        + page((A, "CONTINUED:"), None, (A, "Ela volta."))
        + [(C, 740.0, "(CONTINUED)")],
    ]
    trace = []
    lines = importPages(tmp_path, pages, trace=trace)

    assert "2." not in fountainOf(lines)
    assert "CONTINUED" not in fountainOf(lines)
    assert sorted(r["text"] for r in trace if r["decision"] == "dropped") == [
        "(CONTINUED)",
        "2.",
        "CONTINUED:",
    ]


def testDialogueAcrossPageBreakIsJoined(tmp_path):
    pages = [
        page(
            (A, "INT. CASA - NOITE"),
            None,
            (C, "ANA"),
            (D, "Eu queria dizer que"),
            (C, "(MORE)"),
        ),
        page(
            (C, "ANA (CONT'D)"),
            (D, "nada mudou."),
            None,
            (C, "BETO (CONT'D)"),
            (D, "Mudou sim."),
        ),
    ]
    lines = importPages(tmp_path, pages)

    assert fountainOf(lines) == (
        "INT. CASA - NOITE\n"
        "\n"
        "ANA\n"
        "Eu queria dizer que nada mudou.\n"
        "\n"
        "BETO\n"
        "Mudou sim.\n"
    )


def testSceneNumbersBecomeFountainMarks(tmp_path):
    pages = [[(72.0, 72.0, "12"), (A, 72.0, "INT. CASA - NOITE"), (552.0, 72.0, "12")]]
    lines = importPages(tmp_path, pages)

    assert lines[0].text == "INT. CASA - NOITE #12#"
    assert fountainOf(lines) == "INT. CASA - NOITE #12#\n"


def testDualDialogue(tmp_path):
    rows = [
        [(144.0, "ANA"), (396.0, "BETO")],
        [(108.0, "Você primeiro."), (378.0, "(rindo)")],
        [(108.0, "Não, você."), (360.0, "Juntos, então.")],
        [(360.0, "Os dois.")],
    ]
    top = 84.0
    pg = [(A, 72.0, "INT. CASA - NOITE")]
    top = 96.0
    for row in rows:
        for x, text in row:
            pg.append((x, top, text))
        top += 12.0
    top += 12.0
    pg.append((A, top, "Silêncio."))

    lines = importPages(tmp_path, [pg])

    assert fountainOf(lines) == (
        "INT. CASA - NOITE\n"
        "\n"
        "ANA\n"
        "Você primeiro. Não, você.\n"
        "\n"
        "BETO ^\n"
        "(rindo)\n"
        "Juntos, então. Os dois.\n"
        "\n"
        "Silêncio.\n"
    )


def testTwoColumnsThatAreNotDualDialogueStop(tmp_path):
    pages = [[(A, 72.0, "Ação"), (400.0, 72.0, "solta")]]
    with pytest.raises(pdfimport.PdfImportError) as ei:
        importPages(tmp_path, pages, strict=True)

    assert ei.value.page == 1 and ei.value.lineNo == 1


def testSkipPages(tmp_path):
    pages = [
        [(300.0, 300.0, "TÍTULO")],
        page((A, "INT. CASA - NOITE")),
    ]
    with pytest.raises(pdfimport.PdfImportError):
        importPages(tmp_path, pages, strict=True)

    lines = importPages(tmp_path, pages, skipPages=1, strict=True)
    assert [ln.text for ln in lines] == ["INT. CASA - NOITE"]


def testNoTextIsAnError(tmp_path):
    with pytest.raises(pdfimport.PdfImportError, match="no text"):
        importPages(tmp_path, [[]])


def testProfileErrors():
    with pytest.raises(pdfimport.PdfImportError, match="unknown element"):
        pdfimport.parseProfile({"indent": [{"x": 1, "element": "shot"}]})
    with pytest.raises(pdfimport.PdfImportError, match="exactly one of"):
        pdfimport.parseProfile({"indent": [{"x": 1, "x1": 2, "element": "action"}]})
    with pytest.raises(pdfimport.PdfImportError, match="no \\[\\[indent\\]\\]"):
        pdfimport.parseProfile({})
    # a key after a [[drop]] header belongs to that table in TOML
    with pytest.raises(pdfimport.PdfImportError, match=r"drop\[0\]: unknown key\(s\) character_suffix"):
        pdfimport.parseProfile(
            {
                "indent": [{"x": 1, "element": "action"}],
                "drop": [{"pattern": "x", "character_suffix": ["y"]}],
            }
        )


def testStarterProfilesParse():
    folder = os.path.dirname(TRELBY_PROFILE)
    names = sorted(f for f in os.listdir(folder) if f.endswith(".toml"))
    assert names
    for f in names:
        pdfimport.loadProfile(os.path.join(folder, f))


def testProbe(tmp_path):
    path = makePdf(
        tmp_path / "t.pdf",
        [page((A, "INT. CASA - NOITE"), None, (C, "ANA"), (D, "Oi."), (D, "Tudo bem?"))],
    )
    out = pdfimport.probe(path)
    rows = {}
    for ln in out.splitlines()[3:]:
        if not ln:
            break
        f = ln.split()
        rows[float(f[0])] = int(f[1])

    assert rows == {108.0: 1, 180.0: 2, 252.0: 1}
    assert "p1 l3: Oi." in out
    assert "detected layout:" in out
    assert "  character cues: x=252 (1)" in out


def testTrelbyExportRoundTrip(tmp_path):
    sp = u.load()
    path = tmp_path / "test.pdf"
    path.write_bytes(sp.generatePDF(False))

    profile = pdfimport.loadProfile(TRELBY_PROFILE)
    lines = pdfimport.importPdf(str(path), profile, skipPages=1)
    # compared without whitespace: the fixture has a word longer than the
    # dialogue width, which Trelby's PDF cuts over two lines and the import
    # joins with a space
    got = [(lt, "".join(t.split())) for lt, t in pdfimport.toScreenplay(lines).getElementsAsList()]

    # the six element types the importer knows; Trelby's shots are drawn at
    # the action indent, so they come back as action, and so do scene
    # headings without a scene prefix (scene_action); empty elements draw
    # nothing
    def expected(lt, t):
        if lt == screenplay.SHOT:
            return screenplay.ACTION
        if lt == screenplay.SCENE and not t.upper().startswith(("INT.", "EXT.")):
            return screenplay.ACTION
        return lt

    want = [
        (expected(lt, t), "".join(t.split()))
        for lt, t in sp.getElementsAsList()
        if t.strip()
    ]

    assert got == want


def testCli(tmp_path):
    pdf = makePdf(tmp_path / "cena.pdf", [page((A, "INT. CASA - NOITE"), None, (A, "Escuro."))])
    out = tmp_path / "out"

    assert pdfimport.main(["import", pdf, "--profile", PROFILE, "--out", str(out), "--trace"]) == 0

    assert (out / "cena.fountain").read_text(encoding="utf-8") == "INT. CASA - NOITE\n\nEscuro.\n"
    trace = (out / "cena.trace.tsv").read_text(encoding="utf-8").splitlines()
    assert trace[0] == "page\tline\ttop\tx0\tx1\tdecision\trule\ttext"
    assert trace[1].split("\t")[5:] == ["scene", "x=108", "INT. CASA - NOITE"]


def testCliReportsUnknownIndent(tmp_path, capsys):
    pdf = makePdf(tmp_path / "x.pdf", [page((300.0, "PERDIDO"))])

    assert pdfimport.main(
        ["import", pdf, "--profile", PROFILE, "--out", str(tmp_path), "--trace", "--strict"]
    ) == 1

    assert "page 1, line 1" in capsys.readouterr().err
    assert "UNKNOWN INDENT" in (tmp_path / "x.trace.tsv").read_text(encoding="utf-8")


# File -> Import: myimport.importPdf with a mocked wx (no display)
def _guiImport(tmp_path, monkeypatch, pages, traceDir=None):
    import trelby.myimport as myimport

    wxMock = mock.Mock()
    textDlg = mock.Mock()
    monkeypatch.setattr(myimport, "wx", wxMock)
    monkeypatch.setattr(myimport.misc, "TextDlg", textDlg)
    if traceDir:
        monkeypatch.setenv("MOCAP_WRITER_PDF_TRACE", str(traceDir))
    else:
        monkeypatch.delenv("MOCAP_WRITER_PDF_TRACE", raising=False)

    u.init()
    pdf = makePdf(tmp_path / "gui.pdf", pages)
    return myimport.importPdf(pdf, mock.Mock()), wxMock, textDlg


SCRIPT = [
    page(
        (A, "INT. CASA - NOITE"),
        None,
        (A, "Escuro."),
        None,
        (C, "ANA"),
        (D, "Oi."),
        None,
        (C, "BETO"),
        (P, "(baixo)"),
        (D, "Tudo bem?"),
    )
]


def testGuiImportAsksNothingAndShowsReport(tmp_path, monkeypatch):
    lines, wxMock, textDlg = _guiImport(tmp_path, monkeypatch, SCRIPT)

    assert [ln.text for ln in lines][:2] == ["INT. CASA - NOITE", "Escuro."]
    wxMock.FileDialog.assert_not_called()
    wxMock.MessageBox.assert_not_called()
    report = textDlg.call_args[0][1]
    assert "Layout found in the PDF:" in report
    assert "No issues." in report


def testGuiImportErrorBox(tmp_path, monkeypatch):
    lines, wxMock, textDlg = _guiImport(tmp_path, monkeypatch, [[]])

    assert lines is None
    assert "no text" in wxMock.MessageBox.call_args[0][0]
    textDlg.assert_not_called()


def testGuiImportTrace(tmp_path, monkeypatch):
    lines, wxMock, textDlg = _guiImport(tmp_path, monkeypatch, SCRIPT, traceDir=tmp_path)

    assert lines is not None
    assert (tmp_path / "gui.trace.tsv").exists()
    assert "gui.trace.tsv" in textDlg.call_args[0][1]


def testInlineSceneNumbers(tmp_path):
    profile = pdfimport.loadProfile(PROFILE)
    profile.sceneNumberInline = re.compile(r"^(\d+[A-Z]*)\.\s+")
    path = makePdf(
        tmp_path / "t.pdf",
        [page((A, "7A. INT. CASA - NOITE"), None, (A, "2. Ela conta até dois."))],
    )
    lines = pdfimport.importPdf(path, profile)

    # a number before a scene prefix is a scene number; before anything
    # else it is action text
    assert [(ln.lt, ln.text) for ln in lines] == [
        (screenplay.SCENE, "INT. CASA - NOITE #7A#"),
        (screenplay.ACTION, "2. Ela conta até dois."),
    ]


def testCharacterWithoutSpeechIsAnIssueAndANote(tmp_path):
    issues = []
    trace = []
    lines = importPages(
        tmp_path,
        [page((A, "INT. CASA - NOITE"), None, (C, "ANA"), (A, "Fala digitada como ação."))],
        trace=trace,
        issues=issues,
        notes=True,
    )

    assert [(i.page, i.lineNo) for i in issues] == [(1, 2)]
    assert "character ANA is followed by action" in issues[0].message
    assert trace[-1]["decision"] == "ISSUE"
    # the note goes just before the character cue
    assert [ln.lt for ln in lines] == [
        screenplay.SCENE, screenplay.NOTE, screenplay.CHARACTER, screenplay.ACTION
    ]
    assert lines[1].text.startswith("IMPORT: character ANA")
    assert lines[1].text.endswith("(PDF page 1, line 2)")


def testUnknownIndentIsReadAndNoted(tmp_path):
    issues = []
    lines = importPages(
        tmp_path, [page((A, "INT. CASA - NOITE"), None, (186.0, "Fala torta."))],
        issues=issues, notes=True,
    )

    # 186 is nearest to the dialogue indent (180)
    assert [(ln.lt, ln.text[:20]) for ln in lines] == [
        (screenplay.SCENE, "INT. CASA - NOITE"),
        (screenplay.NOTE, "IMPORT: unusual inde"),
        (screenplay.DIALOGUE, "Fala torta."),
    ]
    assert "(x0 186.0) read as dialogue" in issues[0].message


def testColumnsAreReadAsOneLineAndNoted(tmp_path):
    issues = []
    lines = importPages(tmp_path, [[(A, 72.0, "Ação"), (400.0, 72.0, "solta")]], issues=issues)

    assert [ln.text for ln in lines] == ["Ação solta"]
    assert "2 columns" in issues[0].message


# --- layout detected from the PDF ---


def testDetectedLayoutGivesTheSameScript(tmp_path):
    pages = [
        page(
            (A, "EXT. PRAÇA - DIA"),
            None,
            (A, "Uma praça vazia."),
            None,
            (C, "JOÃO"),
            (P, "(baixo)"),
            (D, "Ninguém veio."),
            None,
            (C, "CONCEIÇÃO"),
            (D, "Ainda é cedo."),
            None,
            (540.0, "CORTA PARA:>"),
        )
    ]
    layout = []
    issues = []
    lines = detectPages(tmp_path, pages, layout=layout, issues=issues)

    assert issues == []
    assert fountainOf(lines) == fountainOf(importPages(tmp_path, pages))
    assert "character cues: x=252 (2)" in layout
    assert "dialogue: x = 180.0" in layout
    assert "parentheticals: x = 216.0" in layout


def testDetectedTitlePagePageNumbersAndMarginSceneNumbers(tmp_path):
    pages = [
        [(250.0, 300.0, "TÍTULO"), (280.0, 330.0, "de Alguém")],
        [
            (72.0, 72.0, "12"), (A, 72.0, "INT. CASA - NOITE"), (552.0, 72.0, "12"),
            (C, 96.0, "ANA"), (D, 108.0, "Eu queria dizer que"), (C, 120.0, "(MORE)"),
        ],
        [(510.0, 36.0, "2."), (C, 72.0, "ANA (CONT'D)"), (D, 84.0, "nada mudou."),
         (A, 108.0, "Ela sai.")],
    ]
    issues = []
    layout = []
    lines = detectPages(tmp_path, pages, issues=issues, layout=layout)

    assert fountainOf([ln for ln in lines if ln.lt != screenplay.NOTE]) == (
        "INT. CASA - NOITE #12#\n"
        "\n"
        "ANA\n"
        "Eu queria dizer que nada mudou.\n"
        "\n"
        "Ela sai.\n"
    )
    assert issues[0].message.startswith("page 1 looks like a title page")
    assert "title page: page 1 (skipped)" in layout
    assert "margin scene numbers: left x = 72.0, right x = 552.0" in layout


def testDetectedNumberedHeadingWithoutIntExt(tmp_path):
    rows = []
    for n in (1, 2, 3):
        rows += [(A, "%d. INT. CASA - NOITE" % n), None, (A, "Algo."), None]
    rows += [(A, "4. - NOITE - RUA"), None, (A, "4. Fim, disse ela.")]
    issues = []
    lines = detectPages(tmp_path, [page(*rows)], issues=issues, notes=False)

    assert [(ln.lt, ln.text) for ln in lines][-2:] == [
        (screenplay.SCENE, "- NOITE - RUA #4#"),
        (screenplay.ACTION, "4. Fim, disse ela."),
    ]
    assert "scene heading 4 has no INT./EXT.; add it" in [i.message for i in issues]


def testDetectedTrelbyExport(tmp_path):
    sp = u.load()
    path = tmp_path / "test.pdf"
    path.write_bytes(sp.generatePDF(False))
    issues = []
    lines = pdfimport.importPdf(str(path), None, issues=issues, notes=False)

    profiled = pdfimport.importPdf(str(path), pdfimport.loadProfile(TRELBY_PROFILE), skipPages=1)
    assert [(ln.lt, ln.text) for ln in lines] == [(ln.lt, ln.text) for ln in profiled]
    assert [i.message[:30] for i in issues] == ["page 1 looks like a title page"]


def testReport():
    text = pdfimport.report(
        "/x/a.pdf", ["dialogue: x = 180.0"], [pdfimport.Issue(2, 3, "something odd")]
    )
    assert text.splitlines()[0] == "a.pdf"
    assert "  dialogue: x = 180.0" in text
    assert "- page 2, line 3: something odd" in text
