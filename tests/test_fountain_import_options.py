# front-matter/import/1: Import -> Fountain options (fountain.importOptions)

import tests.u as u
import trelby.fountain as fountain
import trelby.screenplay as screenplay

TEXT = open(u.fixtureFilePath("fountain/elements.fountain"), encoding="UTF-8").read()


def setup_module():
    u.init()


def body(text):
    return text[text.index("# PRIMEIRO ATO"):]


def test_no_option_changes_nothing():
    assert fountain.importOptions(TEXT) == TEXT


def test_strip_emphasis_in_the_body_only():
    out = fountain.importOptions(TEXT, strip=True)

    assert "Ação com recuo, ênfase e negrito e sublinhado." in out
    assert out.startswith("Title:\n    _**O Teste**_")
    # the boneyard is left alone
    assert "/* um trecho\n   no boneyard */" in out


def test_sections_and_synopses_as_notes_and_act_breaks_kept():
    out = fountain.importOptions(TEXT, notes=True)

    assert "# PRIMEIRO ATO\n\n[[Sequência de abertura]]\n\n[[A casa ainda dorme.]]\n\nINT. SALA" in out
    sp = fountain.load(out, u.new().cfgGl)
    notes = [l.text for l in sp.lines if l.lt == screenplay.NOTE]

    assert "Sequência de abertura" in notes and "A casa ainda dorme." in notes
    assert any(l.lt == screenplay.ACTBREAK for l in sp.lines)


def test_title_lines_as_action():
    out = fountain.importOptions(TEXT, titleAsAction=True)

    assert out.startswith("!Title: O Teste, Segunda linha\n!Credit: Escrito por\n")
    assert "!Contact: Rua Um, 1, alguem@example.com\n\n# PRIMEIRO ATO" in out
    sp = fountain.load(out, u.new().cfgGl)

    assert sp.titles.pages == [] and sp.lines[0].lt == screenplay.ACTION


def test_title_page_dropped():
    out = fountain.importOptions(TEXT, keepTitle=False)

    assert out.startswith("# PRIMEIRO ATO")
    assert body(out) == body(TEXT)
