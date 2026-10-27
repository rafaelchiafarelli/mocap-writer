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
