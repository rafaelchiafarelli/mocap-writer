# film-bible/contract/2: the bible folders (trelby/bible.py)

import json
import os
import shutil
from pathlib import Path

import pytest

import tests.u as u
import trelby.bible as bible
import trelby.film as film
import mocap_contracts as mc

CONTRACTS = Path(__file__).resolve().parents[1] / "third_party" / "mocap-contracts" / "fixtures" / "bible-v1"


def setup_module():
    u.init()


def newBible(root):
    return bible.Bible(film.Film.create(root, ""))


def reopen(b):
    return bible.Bible(film.Film.open(b.film.root))


# one value per map, of each kind the catalog has
VALUES = {
    "set": [("space.int_ext", ["interior"]), ("size.width", [("4.5", "m")]),
            ("continuity.changes", ["broken window"], "2")],
    "character": [("identity.age", [("34", "year")]), ("inner_life.traits", ["calm", "proud"]),
                  ("per_scene.emotional_state", ["tense"], "1")],
    "prop": [("look.color", ["blue"]), ("touch.weight", [("0.3", "kg")]), ("state.state", ["full"], "1.A")],
    "wardrobe": [("piece.garment", ["coat"]), ("hair_makeup.hair", ["wet"], "1")],
}


@pytest.mark.parametrize("map_", bible.MAPS)
def test_write_read_round_trip_per_map(tmp_path, map_):
    b = newBible(tmp_path)
    it = b.create(map_, "Xícara Azul")

    for field, values, *scene in VALUES[map_]:
        b.setValues(it, field, values, "script-stated", "1", "writer", scene=scene[0] if scene else None)

    b.link(it, "1")
    c = reopen(b)
    got = c.get(it.id)

    assert got.msg == it.msg
    assert got.folder == "bible/%s/xicara-azul" % mc.bible.MAP_FOLDERS[map_]
    assert it.id == "%s-w-1" % map_


def test_child_items(tmp_path):
    b = newBible(tmp_path)
    room = b.create("set", "Dining Room")
    table = b.create("set", "Table", parent=room)
    c = reopen(b)

    assert [i.id for i in c.children("set")] == [room.id]
    assert [i.id for i in c.children("set", room.id)] == [table.id]
    assert c.get(table.id).folder == "bible/sets/dining-room/table"

    with pytest.raises(ValueError):
        b.create("prop", "Cup", parent=room)


def test_unknown_field_refused_not_stored(tmp_path):
    b = newBible(tmp_path)
    cup = b.create("prop", "Cup")

    with pytest.raises(KeyError):
        b.setValues(cup, "look.smell", ["x"], "script-stated", "1", "writer")

    cup.msg.values.add(field="look.smell", text="x", state=bible.state("tbd"), source="1",
                       department="props", by="writer", revisit="later")

    with pytest.raises(mc.ContractError, match="not a prop field"):
        b.save(cup)

    assert "look.smell" not in (tmp_path / cup.rel).read_text()


def test_a_wrong_value_is_refused_and_the_item_kept(tmp_path):
    b = newBible(tmp_path)
    cup = b.create("prop", "Cup")

    with pytest.raises(mc.ContractError):
        b.setValues(cup, "ownership.owner", ["prop-w-9"], "script-stated", "1", "writer")

    assert list(cup.msg.values) == []


def test_rename_the_folder_and_the_id_still_resolves(tmp_path):
    b = newBible(tmp_path)
    cup = b.create("prop", "Cup")
    os.rename(tmp_path / cup.folder, tmp_path / "bible/props/renamed-by-hand")

    assert reopen(b).get(cup.id).folder == "bible/props/renamed-by-hand"


def test_rename_moves_the_folder_and_keeps_the_id(tmp_path):
    b = newBible(tmp_path)
    room = b.create("set", "Room")
    b.create("set", "Table", parent=room)
    b.rename(room, "Dining Room")
    c = reopen(b)

    assert c.get(room.id).folder == "bible/sets/dining-room"
    assert c.children("set", room.id)[0].folder == "bible/sets/dining-room/table"


def test_slug_clashes(tmp_path):
    b = newBible(tmp_path)
    a = b.create("prop", "Cup")
    c = b.create("prop", "cup!")
    d = b.create("set", "Photos")
    e = b.create("set", "x", parent=d)
    f = b.create("set", "Photos", parent=d)

    assert [a.folder, c.folder] == ["bible/props/cup", "bible/props/cup-2"]
    assert f.folder == "bible/sets/photos/photos-2"


def test_move_and_delete(tmp_path):
    b = newBible(tmp_path)
    room = b.create("set", "Room")
    table = b.create("set", "Table")
    b.move(table, room)

    assert reopen(b).get(table.id).parent == room.id

    with pytest.raises(ValueError):
        b.move(room, table)

    b.delete(room)
    c = reopen(b)

    assert c.items == {} and not (tmp_path / "bible/sets/room").exists()


def test_files_are_copied_into_the_item(tmp_path):
    b = newBible(tmp_path / "f")
    room = b.create("set", "Room")
    (tmp_path / "plan.png").write_bytes(b"png")
    rel = b.addFile(room, tmp_path / "plan.png", "plans")
    rel2 = b.addFile(room, tmp_path / "plan.png", "plans")
    b.setValues(room, "size.floor_plan", [rel, rel2], "creator-approved", "decision", "creator")

    assert (rel, rel2) == ("plans/plan.png", "plans/plan-2.png")
    assert reopen(b).film.problems == []


def test_a_missing_file_is_a_problem_that_relinks(tmp_path):
    b = newBible(tmp_path)
    room = b.create("set", "Room")
    (tmp_path / "plan.png").write_bytes(b"png")
    b.setValues(room, "size.floor_plan", [b.addFile(room, tmp_path / "plan.png", "plans")],
                "creator-approved", "decision", "creator")
    os.rename(tmp_path / room.folder / "plans", tmp_path / room.folder / "old")
    c = reopen(b)
    (p,) = c.film.problems

    assert p.where == "bible/sets/room/plans/plan.png" and p.ref.kind == "image"

    p.ref.apply("bible/sets/room/old/plan.png")

    assert reopen(b).film.problems == []


def test_approving_a_proposal_changes_its_state_only(tmp_path):
    b = newBible(tmp_path)
    cup = b.create("prop", "Cup")
    b.setValues(cup, "look.color", ["red"], "proposal", "1", "props-continuity-planner")
    (v,) = b.values(cup, "look.color")
    before = mc.BibleValue()
    before.CopyFrom(v)
    b.approve(cup, v)
    (w,) = reopen(b).get(cup.id).msg.values
    before.state = bible.state("creator-approved")

    assert w == before


def test_links_and_scenes(tmp_path):
    b = newBible(tmp_path)
    coat = b.create("wardrobe", "Coat")
    ana = b.create("character", "Ana")
    b.link(coat, "1", ana.id)
    b.link(coat, "1", ana.id)
    b.setValues(coat, "hair_makeup.hair", ["wet"], "script-stated", "2", "writer", scene="2")

    assert b.scenes(coat) == {"1", "2"} and len(coat.msg.links) == 1

    with pytest.raises(mc.ContractError):
        b.link(ana, "3", coat.id)

    b.unlink(coat, "1", ana.id)

    assert len(reopen(b).get(coat.id).msg.links) == 0


def test_invalid_and_misplaced_items_are_problems(tmp_path):
    b = newBible(tmp_path)
    (tmp_path / "bible/props/bad").mkdir(parents=True)
    (tmp_path / "bible/props/bad/item.json").write_text("{}")
    (tmp_path / "bible/props/set-here").mkdir()
    shutil.copy(CONTRACTS / "sets/dining-room/item.json", tmp_path / "bible/props/set-here/item.json")
    c = reopen(b)

    assert [p.where for p in c.film.problems] == [
        "bible/props/bad/item.json", "bible/props/set-here/item.json"]
    assert c.items == {}


def test_the_contracts_fixture_reads(tmp_path):
    b = newBible(tmp_path)
    shutil.rmtree(tmp_path / "bible")
    shutil.copytree(CONTRACTS, tmp_path / "bible", ignore=shutil.ignore_patterns("invalid"))
    c = reopen(b)

    assert sorted(c.items) == ["character-w-1", "prop-pcp-1", "set-w-1", "set-w-3", "wardrobe-w-1"]
    assert c.notProps == ["OK", "TV"]
    assert [p.where for p in c.film.problems] == ["bible/sets/dining-room/plans/floor.png"]


def test_writes_are_logged(tmp_path):
    b = newBible(tmp_path)
    b.create("prop", "Cup")

    assert [c.record for c in b.film.changes()] == ["prop-w-1"]


def test_not_props(tmp_path):
    b = newBible(tmp_path)
    b.notProps.append("TV")
    b.saveNotProps()

    assert reopen(b).notProps == ["TV"]
