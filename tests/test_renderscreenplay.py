import tests.u as u
import trelby.util as util


def testRenderScreenplay() -> None:
    sp = u.load()
    data = sp.generatePDF(True)

    assert len(data) > 200
    assert data[:8] == util.toLatin1("%PDF-1.5")


def testRenderScreenplayWithCustomFont() -> None:
    sp = u.load()
    for pfi in sp.cfg.getPDFFontIds():
        pf = sp.cfg.getPDFFont(pfi)
        pf.pdfName = "Jost"
        pf.filename = u.fixtureFilePath("custom-font/Jost-400-Book.ttf")

    data = sp.generatePDF(True)

    assert len(data) > 200
    assert data[:8] == util.toLatin1("%PDF-1.5")


# a custom PDF font with no file, or a file that is not a font, is an error
# the GUI can show, not a bare Exception (bugs/import-export/10)
def testUnusableCustomFontIsMiscError(tmp_path) -> None:
    import pytest

    import trelby.error as error
    import trelby.pdf as pdf
    import trelby.pml as pml

    sp = u.load()
    notAFont = tmp_path / "x.ttf"
    notAFont.write_bytes(b"not a font")
    for pfi in sp.cfg.getPDFFontIds():
        pf = sp.cfg.getPDFFont(pfi)
        pf.pdfName = "NotAFontAnywhere"
        pf.filename = str(notAFont)

    with pytest.raises(error.MiscError):
        sp.generatePDF(True)

    # a name with no file (the script settings never send one; pdf.py
    # still checks)
    doc = sp.generatePML(True)
    for style in list(doc.fonts):
        doc.fonts[style] = pml.PDFFontInfo("NoSuchFontAnywhere", "")

    with pytest.raises(error.MiscError):
        pdf.generate(doc)


# Helvetica and Times have Latin-1 width tables; other characters (pasted
# or imported into a title page) are measured like "?"
# (bugs/import-export/7)
def testNonLatin1WidthInCoreFonts() -> None:
    import trelby.fontinfo as fontinfo
    import trelby.pml as pml

    fm = fontinfo.getMetrics(pml.HELVETICA)

    assert fm.getTextWidth("Ł", 12) == fm.getTextWidth("?", 12)
    assert fm.getTextWidth("AŁ", 12) > fm.getTextWidth("A", 12)


# "Open PDF on current page": the printed PDF's /OpenAction goes to the
# cursor's page; an export has none (bugs/import-export/9)
def testOpenOnCurrentPage() -> None:
    import io

    import pdfplumber
    from pdfminer.pdftypes import resolve1

    sp = u.load()
    sp.cfg.pdfOpenOnCurrentPage = True
    sp.line = sp.page2lines(3)[0]

    with pdfplumber.open(io.BytesIO(sp.generatePDF(False))) as pdf:
        dest = resolve1(pdf.doc.catalog["OpenAction"])
        ids = [p.page_obj.pageid for p in pdf.pages]

        # title page first, then script page 3
        assert ids.index(dest[0].objid) == len(sp.titles.pages) + 2

    with pdfplumber.open(io.BytesIO(sp.generatePDF(True))) as pdf:
        assert "OpenAction" not in pdf.doc.catalog
