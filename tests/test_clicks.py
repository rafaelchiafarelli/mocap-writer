# bugs/editor/14-16: two clicks select the word, three the element

import tests.u as u
from trelby.clicks import ClickCounter


def test_counting():
    c = ClickCounter()

    assert [c.click(0.0, 1), c.click(0.2, 1), c.click(0.4, 1)] == [1, 2, 3]
    assert c.click(1.5, 1) == 1
    assert c.click(1.6, 2) == 1


def test_gtk_double_click_after_the_second_press_is_the_same_click():
    c = ClickCounter()

    assert [c.click(0.0, 1), c.click(0.2, 1), c.click(0.21, 1, True), c.click(0.4, 1)] == [1, 2, 2, 3]


def test_a_double_click_alone_counts_two():
    c = ClickCounter()

    assert [c.click(0.0, 1, True), c.click(0.1, 1)] == [2, 3]


def selected(sp):
    return "\n".join(l.text for l in sp.getSelectedAsCD(False).lines)


def test_select_word():
    sp = u.loadString("INT. ROOM - DAY\n\nShe picks up the BLUE CUP.\n")
    i = [n for n, l in enumerate(sp.lines) if "BLUE" in l.text][0]
    text = sp.lines[i].text

    assert sp.selectWordAt(i, text.index("BLUE") + 2) and selected(sp) == "BLUE"
    assert sp.selectWordAt(i, text.index("CUP") + 3) and selected(sp) == "CUP"
    assert sp.selectWordAt(i, 0) and selected(sp) == "She"
    assert sp.selectWordAt(i, text.index(" up")) and selected(sp) == "picks"

    sp = u.loadString("INT. ROOM - DAY\n\nA  -- b\n")
    j = [n for n, l in enumerate(sp.lines) if "--" in l.text][0]
    sp.clearMark()

    assert not sp.selectWordAt(j, sp.lines[j].text.index("-") + 1) and sp.mark is None


def test_select_element():
    sp = u.loadString("INT. ROOM - DAY\n\n" + "word " * 40 + "end.\n\nNext.\n")
    first = [n for n, l in enumerate(sp.lines) if l.text.startswith("word")][0]
    _f, last = sp.getElemIndexesFromLine(first)

    assert last > first  # the Action wraps over several lines
    sp.selectElementAt(last)

    assert selected(sp).replace("\n", " ").split() == ("word " * 40 + "end.").split()
