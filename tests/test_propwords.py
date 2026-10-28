from trelby.propwords import find_prop_words

# props in Action lines (editor-ux/typing/2): a prop is a run of
# consecutive fully capitalized words (film-bible/links/2).


def words(line, typingAt=None):
    return [w for _, _, w in find_prop_words(line, typingAt)]


def testPositions():
    line = "She sits on the CHAIR."

    assert find_prop_words(line) == [(16, 21, "CHAIR")]
    assert line[16:21] == "CHAIR"


def testAccents():
    assert words("Ela senta na CADEIRA sob a LÂMPADA.") == ["CADEIRA", "LÂMPADA"]
    assert words("O CORAÇÃO e a MÃE") == ["CORAÇÃO", "MÃE"]


def testMultiWordRunIsOneProp():
    assert words("Ela pega a XÍCARA AZUL e sai.") == ["XÍCARA AZUL"]
    assert find_prop_words("a XÍCARA AZUL") == [(2, 13, "XÍCARA AZUL")]


def testPunctuationEndsARun():
    assert words("XÍCARA. AZUL") == ["XÍCARA", "AZUL"]
    assert words('"KNIFE", (ROPE) ...LAMP! BOX?') == ["KNIFE", "ROPE", "LAMP", "BOX"]


def testOneLetterCapitalsInsideARun():
    assert words("a CAIXA DE FÓSFORO aqui") == ["CAIXA DE FÓSFORO"]
    assert words("a CAIXA E VELA aqui") == ["CAIXA E VELA"]
    assert words("a CAIXA de FÓSFORO aqui") == ["CAIXA", "FÓSFORO"]
    assert words("a CAIXA e VELA aqui") == ["CAIXA", "VELA"]


def testOneLetterWordsNeverStartOrEndARun():
    assert words("I see A cat and a TV") == ["TV"]
    assert words("O X marks it") == []
    assert words("A TV E") == ["TV"]


def testHyphenAndApostropheJoinAWord():
    assert words("A WALKIE-TALKIE and O'BRIEN") == ["WALKIE-TALKIE", "O'BRIEN"]


def testMixedCaseAndDigits():
    assert words("McDONALD and Chair and iPHONE") == []
    assert words("the TV2 and R2D2") == ["TV"]
    assert words("") == []


def testAllCapsLine():
    assert words("THE DOOR OPENS.") == ["THE DOOR OPENS"]


def testARunBeingTypedIsNotOfferedYet():
    assert words("Ela pega a XÍCARA AZ", typingAt=20) == []
    assert words("Ela pega a XÍCARA AZUL e", typingAt=24) == ["XÍCARA AZUL"]
    assert words("Ela pega a XÍCARA AZUL.", typingAt=23) == ["XÍCARA AZUL"]
    assert words("Ela pega a XÍCARA", typingAt=3) == ["XÍCARA"]
