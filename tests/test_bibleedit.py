# film-bible/maps/1-4: what the bible form edits (trelby/bibleedit.py)

import datetime

import pytest

import tests.u as u
import trelby.bible as bible
import trelby.bibleedit as bibleedit
import trelby.film as film
import mocap_contracts as mc

TODAY = datetime.date(2026, 10, 28)


def setup_module():
    u.init()


def newBible(root):
    return bible.Bible(film.Film.create(root, "INT. ROOM - DAY\n"))


def reopen(b):
    return bible.Bible(film.Film.open(b.film.root))


@pytest.mark.parametrize("map_", bible.MAPS)
def test_every_catalog_field_of_the_map_is_in_the_form(map_):
    names = [f.name for g in bibleedit.groups(map_) for f in g.fields]

    assert names == list(mc.bible.fields(map_))
    assert [g.key for g in bibleedit.groups(map_)][0] == "general"


# one text field, one number, one choice, one list per map
EDITS = {
    "set": [("space.period", "1970s"), ("size.width", "4,5"), ("space.int_ext", "interior"),
            ("space.time_of_day", "night; dawn")],
    "character": [("identity.occupation", "nurse"), ("identity.age", "34"),
                  ("identity.role", "protagonist"), ("inner_life.traits", "calm; proud")],
    "prop": [("look.color", "blue"), ("touch.weight", "0.3"), ("look.material", "enamel"),
             ("general.tags", "kitchen")],
    "wardrobe": [("piece.garment", "coat"), ("realization.duplicates", "2"),
                 ("condition.condition", "wet"), ("general.tags", "rain")],
}


@pytest.mark.parametrize("map_", bible.MAPS)
def test_edit_save_reopen(tmp_path, map_):
    b = newBible(tmp_path)
    it = b.create(map_, "Item")

    for name, s in EDITS[map_]:
        assert bibleedit.commit(b, it, name, s, today=TODAY)

    c = reopen(b)
    got = c.get(it.id)

    for name, s in EDITS[map_]:
        assert bibleedit.text(c, got, name) == s.replace(",", ".")
        assert bibleedit.stateOf(c, got, name) == "creator-approved"

    v = c.values(got, EDITS[map_][0][0])[0]
    assert (v.source, v.by) == ("creator 2026-10-28", "creator")


def test_an_unchanged_value_is_not_saved_again(tmp_path):
    b = newBible(tmp_path)
    it = b.create("prop", "Cup")
    bibleedit.commit(b, it, "look.color", "blue")

    assert not bibleedit.commit(b, it, "look.color", " blue ")
    assert bibleedit.commit(b, it, "look.color", "")
    assert b.values(it, "look.color") == []


def test_a_bad_number_is_refused(tmp_path):
    b = newBible(tmp_path)
    it = b.create("prop", "Cup")

    with pytest.raises(ValueError):
        bibleedit.commit(b, it, "touch.weight", "heavy")


def test_approving_a_proposal_changes_its_state_only(tmp_path):
    b = newBible(tmp_path)
    it = b.create("prop", "Cup")
    b.setValues(it, "look.color", ["red"], "proposal", "12", "props-continuity-planner")
    before = mc.BibleValue()
    before.CopyFrom(b.values(it, "look.color")[0])
    bibleedit.setState(b, it, "look.color", "creator-approved")
    after = reopen(b).get(it.id).msg.values[0]
    before.state = bible.state("creator-approved")

    assert after == before


def test_tbd_needs_its_revisit_and_script_stated_its_scene(tmp_path):
    b = newBible(tmp_path)
    it = b.create("prop", "Cup")
    bibleedit.commit(b, it, "look.color", "red")

    with pytest.raises(mc.ContractError):
        bibleedit.setState(b, it, "look.color", "tbd")

    assert bibleedit.stateOf(b, it, "look.color") == "creator-approved"

    bibleedit.setState(b, it, "look.color", "tbd", revisit="after the color test")
    bibleedit.setState(b, it, "look.color", "script-stated", source="12")
    v = reopen(b).get(it.id).msg.values[0]

    assert (bible.stateName(v.state), v.source, v.HasField("revisit")) == ("script-stated", "12", False)


def test_per_scene_values(tmp_path):
    b = newBible(tmp_path)
    it = b.create("character", "Ana")
    bibleedit.commit(b, it, "per_scene.emotional_state", "calm", scene="1")
    bibleedit.commit(b, it, "per_scene.emotional_state", "angry", scene="2")

    assert bibleedit.text(b, it, "per_scene.emotional_state", "2") == "angry"
    assert bibleedit.sceneChoices(b, it) == ["1", "2"]


def test_links_show_names_and_keep_notes(tmp_path):
    b = newBible(tmp_path)
    ana = b.create("character", "Ana")
    bia = b.create("character", "Bia")
    cid = b.create("character", "Cid")

    assert bibleedit.linkChoices(b, ana, "relationships.with") == [(bia.id, "Bia"), (cid.id, "Cid")]

    bibleedit.setLinks(b, ana, "relationships.with", [bia.id])
    b.values(ana, "relationships.with")[0].note = "sister"
    bibleedit.setLinks(b, ana, "relationships.with", [bia.id, cid.id])

    assert bibleedit.text(b, ana, "relationships.with") == "Bia; Cid"
    assert b.values(ana, "relationships.with")[0].note == "sister"


def test_files_are_added_and_removed(tmp_path):
    b = newBible(tmp_path / "f")
    room = b.create("set", "Room")
    (tmp_path / "a.png").write_bytes(b"x")
    bibleedit.addFiles(b, room, "size.floor_plan", [tmp_path / "a.png", tmp_path / "a.png"])

    assert bibleedit.text(b, room, "size.floor_plan") == "plans/a.png; plans/a-2.png"

    bibleedit.removeFile(b, room, "size.floor_plan", "plans/a.png")

    assert bibleedit.text(b, room, "size.floor_plan") == "plans/a-2.png"
    assert not (tmp_path / "f" / room.folder / "plans/a.png").exists()


def test_describe(tmp_path):
    b = newBible(tmp_path)
    it = b.create("prop", "Cup")

    assert bibleedit.describe(b, it, "look.color") == "No value yet."

    b.setValues(it, "look.color", ["red"], "tbd", "12", "writer", revisit="later")

    assert "Revisit when: later" in bibleedit.describe(b, it, "look.color")
