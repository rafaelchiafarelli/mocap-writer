# fountain-native/notes/1: annotations anchored to the script (trelby/annotations.py)

import pytest

import tests.u as u
import trelby.annotations as annotations
import trelby.film as film
import trelby.fountain as fountain
import trelby.scenenumbers as scenenumbers
import mocap_contracts as mc

SCRIPT = """\
INT. ROOM - DAY #1#

She runs down the street, fast. Then she stops and waits for the long bus to come around.

ANA
I told you.

EXT. STREET - NIGHT #2#

Rain.
"""


def setup_module():
    u.init()


def setup(tmp_path, text=SCRIPT):
    f = film.Film.create(tmp_path, text)

    return annotations.Annotations(f), u.loadString(text)


def spanText(sp, place):
    return "".join(sp.lines[l].text[c1:c2] for l, c1, c2 in place.spans)


def actionLine(sp, word):
    return [i for i, l in enumerate(sp.lines) if word in l.text][0]


def test_a_span_inside_one_line(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("note", "1", 1, "runs down the street", 1, "Faster.")
    p = an.resolve(sp)[a.id]

    assert spanText(sp, p) == "runs down the street" and p.attached


def test_a_span_across_wrapped_lines(tmp_path):
    an, sp = setup(tmp_path)
    first, last = sp.getElemIndexesFromLine(actionLine(sp, "runs"))
    assert last > first  # the Action wraps
    quote = "waits for the long bus"
    a = an.add("note", "1", 1, quote, 1)
    p = an.resolve(sp)[a.id]

    assert spanText(sp, p).replace(" ", "") == quote.replace(" ", "")


def test_a_whole_element_and_a_whole_scene(tmp_path):
    an, sp = setup(tmp_path)
    el = an.add("character_direction", "1", 3)
    sc = an.add("general_direction", "2")
    places = an.resolve(sp)

    assert spanText(sp, places[el.id]) == "I told you."
    assert places[sc.id].spans == [] and sp.lines[places[sc.id].line].text == "EXT. STREET - NIGHT"


def test_typing_before_a_span_keeps_it(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("note", "1", 1, "the street", 1)
    i = actionLine(sp, "runs")
    sp.lines[i].text = "Today " + sp.lines[i].text
    sp.reformatAll()

    assert spanText(sp, an.resolve(sp)[a.id]) == "the street"


def test_an_element_inserted_before_keeps_the_annotation_on_its_element(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("character_direction", "1", 3)
    an.resolve(sp)
    sp2 = u.loadString(SCRIPT.replace("ANA\n", "A door opens.\n\nANA\n"))

    assert spanText(sp2, an.resolve(sp2)[a.id]) == "I told you."
    assert a.anchor.element == 4


def test_editing_inside_the_quote_follows_it(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("note", "1", 1, "runs down the street", 1)
    an.resolve(sp)
    sp2 = u.loadString(SCRIPT.replace("runs down the street", "runs down the wet street"))
    p = an.resolve(sp2)[a.id]

    assert "street" in spanText(sp2, p) and a.anchor.quote != "runs down the street"


def test_deleting_the_quote_moves_it_to_the_element(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("note", "1", 3, "told", 1)
    an.resolve(sp)
    sp2 = u.loadString(SCRIPT.replace("I told you.", "Hm."))
    p = an.resolve(sp2)[a.id]

    assert spanText(sp2, p) == "Hm." and not a.anchor.HasField("quote")
    assert a.id in an.dirty


def test_deleting_the_element_moves_it_to_the_scene(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("character_direction", "1", 3)
    an.resolve(sp)
    sp2 = u.loadString(SCRIPT.replace("ANA\nI told you.\n\n", ""))
    p = an.resolve(sp2)[a.id]

    assert p.spans == [] and not a.anchor.HasField("element")


def test_edited_elsewhere_the_quote_is_found_again_or_unattached(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("note", "1", 1, "runs down the street", 1)
    b = an.add("note", "1", 1, "the long bus", 1)
    other = SCRIPT.replace("She runs", "First line.\n\nShe runs").replace("the long bus", "a taxi")
    an2 = annotations.Annotations(film.Film.open(tmp_path))
    places = an2.resolve(u.loadString(other), editing=False)

    assert places[a.id].attached and an2.records[a.id].anchor.element == 2
    assert not places[b.id].attached and an2.records[b.id].anchor.quote == "the long bus"


def test_a_scene_gone_keeps_its_number(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("note", "2", 1)
    head = [l for l, n in scenenumbers.scenesOf(sp) if n == "2"][0]
    sp.setMark(head, 0)
    sp.line, sp.column = len(sp.lines) - 1, len(sp.lines[-1].text)
    sp.getSelectedAsCD(True)  # the user deletes scene 2
    p = an.resolve(sp)[a.id]

    assert not p.attached and a.anchor.scene == "2"

    scenenumbers.prepareSave(sp)  # the scene's number becomes its OMITTED heading
    p = an.resolve(sp)[a.id]

    assert p.attached and sp.lines[p.line].text == "OMITTED"


def test_the_fountain_file_is_never_touched(tmp_path):
    an, sp = setup(tmp_path)
    before = (tmp_path / "script.fountain").read_bytes()
    an.add("note", "1", 1, "the street", 1, "x")
    an.resolve(sp)
    an.flush()

    assert (tmp_path / "script.fountain").read_bytes() == before
    assert fountain.generate(sp).text == fountain.generate(u.loadString(SCRIPT)).text


def test_records_round_trip_and_flush_writes_moved_anchors(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("character_direction", "1", 3, text="Looks away.")
    an.resolve(sp)
    sp2 = u.loadString(SCRIPT.replace("ANA\n", "A door opens.\n\nANA\n"))
    an.resolve(sp2)
    an.flush()
    an2 = annotations.Annotations(film.Film.open(tmp_path))

    assert an2.records[a.id].anchor.element == 4 and an2.records[a.id].text == "Looks away."


def test_shots_are_numbered_per_scene_and_never_reused(tmp_path):
    an, sp = setup(tmp_path)
    s1 = an.add("shot", "1", 1)
    s2 = an.add("shot", "1", 3)
    an.delete(s2.id)
    s3 = an.add("shot", "1", 1)
    t1 = an.add("shot", "2", 1)

    assert [s1.shot, s3.shot, t1.shot] == [1, 3, 1]
    assert "1 S3" in an.describe(s3)


def test_renamed_scenes(tmp_path):
    an, sp = setup(tmp_path)
    a = an.add("shot", "1", 1)
    an.renameScenes({"1": "3"})
    an2 = annotations.Annotations(film.Film.open(tmp_path))

    assert an2.records[a.id].anchor.scene == "3"
    assert an2.nextShot("3") == 2


def test_the_anchor_of_a_selection(tmp_path):
    _an, sp = setup(tmp_path)
    i = actionLine(sp, "runs")
    text = sp.lines[i].text
    sp.line, sp.column = i, text.index("runs")
    sp.cmd("setMark")
    sp.column = text.index("street") + len("street") - 1

    assert annotations.anchorAt(sp) == ("1", 1, "runs down the street", 1)

    sp.clearMark()

    assert annotations.anchorAt(sp) == ("1", 1, None, None)
