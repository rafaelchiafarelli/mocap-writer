from trelby.propwords import find_prop_words

# capitalized words in Action lines (editor-ux/typing/2): the detection
# film-bible reuses to create prop records.


def words(line):
    return [w for _, _, w in find_prop_words(line)]


def testPositions():
    line = "She sits on the CHAIR."

    assert find_prop_words(line) == [(16, 21, "CHAIR")]
    assert line[16:21] == "CHAIR"


def testAccents():
    assert words("Ela senta na CADEIRA sob a LÂMPADA.") == ["CADEIRA", "LÂMPADA"]
    assert words("O CORAÇÃO e a MÃE") == ["CORAÇÃO", "MÃE"]


def testShortWordsIgnored():
    assert words("I see A cat and a TV") == ["TV"]
    assert words("O X marks it") == []


def testPunctuation():
    assert words('"KNIFE", (ROPE) ...LAMP! BOX?') == ["KNIFE", "ROPE", "LAMP", "BOX"]
    assert words("A WALKIE-TALKIE and O'BRIEN") == ["WALKIE", "TALKIE", "BRIEN"]


def testMixedCaseAndDigits():
    assert words("McDONALD and Chair and iPHONE") == []
    assert words("the TV2 and R2D2") == ["TV"]
    assert words("") == []


def testAllCapsLine():
    assert words("THE DOOR OPENS.") == ["THE", "DOOR", "OPENS"]
