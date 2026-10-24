import trelby.config as config
import trelby.fountain as fountain
import trelby.screenplay as scr
import trelby.translations as translations
import tests.u as u

_ = translations.trelby_translations_load()

# Fountain as the native format (fountain-native/io/1): open -> save -> open
# is byte-identical, edits rewrite only what they touch.


def fixture(name):
    with open(u.fixtureFilePath("fountain/" + name), "rb") as f:
        return f.read().decode("UTF-8")


def load(text):
    u.init()

    return fountain.load(text, config.ConfigGlobal())


def save(sp):
    res = fountain.generate(sp)
    sp.fountainSource = res.source

    return res


def roundTrip(text):
    sp = load(text)
    res = save(sp)

    assert res.text == text
    assert res.lost == []

    # and once more from what was saved
    assert save(load(res.text)).text == text


def elems(sp):
    return fountain.elementsOf(sp)


def testSampleRoundTrip():
    roundTrip(fixture("sample_ptbr.fountain"))


def testElementsRoundTrip():
    roundTrip(fixture("elements.fountain"))


def testNoFinalNewline():
    roundTrip(fixture("no-final-newline.fountain"))


def testCrlfAndBom():
    text = "﻿" + fixture("elements.fountain").replace("\n", "\r\n")
    roundTrip(text)

    assert load(text).fountainSource.eol == "\r\n"


def testEmptyFile():
    sp = load("")

    assert elems(sp) == [(scr.SCENE, "")]
    assert sp.titles.pages == []
    assert save(sp).text == ""


def testSampleElements():
    sp = load(fixture("sample_ptbr.fountain"))

    assert elems(sp) == [
        (scr.ACTBREAK, "ATO 1"),
        (scr.SCENE, "INT. COZINHA - NOITE"),
        (scr.ACTION, "João entra, larga a XÍCARA na mesa. [[prop: xícara azul]]"),
        (scr.CHARACTER, "JOÃO"),
        (scr.PAREN, "(cansado)"),
        (scr.DIALOGUE, "Você ainda está acordada?"),
        (scr.CHARACTER, "MARIA"),
        (scr.DIALOGUE, "Sempre."),
        (scr.ACTION, "CENA 13 - QUINTAL - DIA"),
        (scr.SCENE, "QUINTAL - DIA"),
        (scr.CHARACTER, "ÂNGELA"),
        (scr.DIALOGUE, "Oi."),
    ]

    src = sp.fountainSource
    assert src.elements[1].decor == " #12#"
    assert src.elements[6].decor == " ^"
    assert "= João chega em casa tarde." in src.elements[1].pre


def testEveryElement():
    sp = load(fixture("elements.fountain"))

    assert elems(sp) == [
        (scr.ACTBREAK, "PRIMEIRO ATO"),
        (scr.SCENE, "INT. SALA - NOITE"),
        (
            scr.ACTION,
            "Uma luz acende. Ninguém está aqui.\nUma segunda linha da mesma ação.",
        ),
        (
            scr.ACTION,
            "    Ação com recuo, *ênfase* e **negrito** e _sublinhado_.",
        ),
        (scr.ACTION, "FORÇADA EM MAIÚSCULAS\ncontinua aqui."),
        (scr.CHARACTER, "ANA (V.O.)"),
        (scr.PAREN, "(baixinho)"),
        (scr.DIALOGUE, "Primeira linha.\n\nDepois de uma linha vazia."),
        (scr.PAREN, "(pausa)"),
        (scr.DIALOGUE, "Última."),
        (scr.CHARACTER, "BRUNO"),
        (scr.DIALOGUE, "Ao mesmo tempo."),
        (scr.CHARACTER, "mcCLANE"),
        (scr.DIALOGUE, "Yippee."),
        (scr.TRANSITION, "CUT TO:"),
        (scr.TRANSITION, "FADE OUT."),
        (scr.ACTION, ">CENTRADO<"),
        (scr.SHOT, "CLOSE NA MÃO"),
        (scr.NOTE, "uma nota sozinha"),
        (scr.NOTE, "nota em\nduas linhas"),
        (scr.SCENE, "EXT. QUINTAL - DIA"),
        (scr.SCENE, "FLASHBACK"),
        (
            scr.ACTION,
            "Ação com [[nota inline]] e /* boneyard inline */ dentro.",
        ),
        (scr.ACTION, "FADE TO BLACK."),
    ]


def testTitlePage():
    sp = load(fixture("elements.fountain"))
    page = sp.titles.pages[0]

    assert page[0].items == ["O Teste", "Segunda linha"]
    assert page[0].isBold
    assert ["Credit: Escrito por"] in [ts.items for ts in page]
    assert ["by", "", "Alguém"] in [ts.items for ts in page]
    assert ["Draft date: 2026-10-24"] in [ts.items for ts in page]
    assert ["Rua Um, 1", "alguem@example.com"] in [ts.items for ts in page]


def testEditedTitlePage():
    sp = load(fixture("sample_ptbr.fountain"))
    sp.titles.pages[0][0].items = ["Outro"]

    text = save(sp).text

    assert text.startswith("Title: Outro\nAuthor: Rafael\n\n# ATO 1\n")
    assert load(text).titles.pages[0][0].items == ["Outro"]


def testHiddenSourceKept():
    text = fixture("elements.fountain")
    src = load(text).fountainSource
    hidden = "".join(e.pre for e in src.elements) + src.tail

    for s in (
        "## Sequência de abertura",
        "= A casa ainda dorme.",
        "/* um trecho\n   no boneyard */",
        "===",
    ):
        assert s in hidden


def findLine(sp, text):
    for i, ln in enumerate(sp.lines):
        if ln.text.startswith(text):
            return i

    raise AssertionError(text)


def testEditOneElement():
    text = fixture("elements.fountain")
    sp = load(text)
    sp.lines[findLine(sp, "Ao mesmo")].text = "Ao mesmo tempo, de novo."

    res = save(sp)

    assert res.lost == []
    assert res.text == text.replace("Ao mesmo tempo.", "Ao mesmo tempo, de novo.")


def testEditedSceneKeepsNumber():
    sp = load(fixture("sample_ptbr.fountain"))
    sp.lines[findLine(sp, "INT. COZINHA")].text = "INT. COZINHA - DIA"

    text = save(sp).text

    assert "\nINT. COZINHA - DIA #12#\n" in text
    assert "= João chega em casa tarde.\n\nINT. COZINHA - DIA" in text


def testEditedCueKeepsDualMark():
    sp = load(fixture("sample_ptbr.fountain"))
    sp.lines[findLine(sp, "MARIA")].text = "MARIANA"

    assert "\nMARIANA ^\nSempre.\n" in save(sp).text


def testInsertAndDelete():
    text = fixture("elements.fountain")
    sp = load(text)

    # a new action after the scene heading
    i = findLine(sp, "INT. SALA")
    sp.lines.insert(i + 1, scr.Line(scr.LB_LAST, scr.ACTION, "Nova ação."))

    # the action before the boneyard goes away: the boneyard stays
    i = findLine(sp, "FORÇADA")
    while sp.lines[i].lb != scr.LB_LAST:
        del sp.lines[i]
    del sp.lines[i]

    res = save(sp)
    out = res.text

    assert res.lost == []
    assert "INT. SALA - NOITE #1#\n\nNova ação.\n\nUma luz acende." in out
    assert "FORÇADA" not in out
    assert "/* um trecho\n   no boneyard */" in out
    assert "ANA (V.O.)\n(baixinho)\n" in out

    # what was saved reads back the same
    assert elems(load(out)) == [
        (lt, t) for lt, t in elems(sp) if t.strip()
    ]


def testForcedWhenNeeded():
    sp = load("")
    sp.lines = [
        scr.Line(scr.LB_LAST, scr.SCENE, "flashback"),
        scr.Line(scr.LB_FORCED, scr.ACTION, "BANG!"),
        scr.Line(scr.LB_LAST, scr.ACTION, "A porta abre."),
        scr.Line(scr.LB_LAST, scr.CHARACTER, "ana"),
        scr.Line(scr.LB_LAST, scr.DIALOGUE, "Oi."),
        scr.Line(scr.LB_LAST, scr.TRANSITION, "fade out."),
        scr.Line(scr.LB_LAST, scr.ACTION, "Nota: isto é ação."),
    ]
    # an action that looks like a title key is only a problem at the top
    sp.lines.insert(0, scr.Line(scr.LB_LAST, scr.ACTION, "Lugar: casa"))

    res = save(sp)

    assert res.lost == []
    assert res.text == (
        "!Lugar: casa\n\n"
        ".FLASHBACK\n\n"
        "!BANG!\nA porta abre.\n\n"
        "ANA\nOi.\n\n"
        "> FADE OUT.\n\n"
        "Nota: isto é ação.\n"
    )


def testLostReported():
    sp = load("")
    sp.lines = [
        scr.Line(scr.LB_LAST, scr.ACTION, "Ação."),
        scr.Line(scr.LB_LAST, scr.DIALOGUE, "Sem personagem."),
    ]

    assert save(sp).lost == [(scr.DIALOGUE, "Sem personagem.")]


def testFromTrelby():
    sp = u.load()
    res = save(sp)

    # test.trelby has a dialogue split by an empty action: Fountain cannot
    # tell the two apart
    assert res.lost == [(scr.DIALOGUE, "Very."), (scr.DIALOGUE, "Very")]

    back = load(res.text)
    assert len(elems(back)) == len([e for e in elems(sp) if e[1].strip()]) - 1
    assert save(back).text == res.text


def testWrappedLinesJoin():
    # long lines are wrapped by the editor and joined again on save
    long = "palavra " * 40
    text = "EXT. RUA - DIA\n\n" + long.strip() + "\n"
    sp = load(text)

    assert len(sp.lines) > 3
    assert save(sp).text == text


def testIsFountain():
    assert fountain.isFountain("a/b.fountain")
    assert fountain.isFountain("B.FOUNTAIN")
    assert not fountain.isFountain("b.trelby")
