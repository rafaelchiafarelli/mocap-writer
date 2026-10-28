# file-format/layout/5: the change log (trelby/film.py)

import json

import tests.u as u
import trelby.film as film
import mocap_contracts as mc


def setup_module():
    u.init()


def item(name):
    return json.dumps({"id": "prop-w-1", "name": name}) + "\n"


REL = "bible/props/cup/item.json"


def lines(root):
    return [json.loads(line) for p in sorted((root / "history").glob("*.jsonl"))
            for line in p.read_text().splitlines()]


def test_create_update_delete_each_log_one_line(tmp_path):
    f = film.Film.create(tmp_path)
    f.writeText(REL, item("Cup"))
    f.writeText(REL, item("Blue Cup"))
    f.deleteFile(REL)

    log = lines(tmp_path)

    assert [c["op"] for c in log] == ["CHANGE_OP_CREATE", "CHANGE_OP_UPDATE", "CHANGE_OP_DELETE"]
    assert [c["record"] for c in log] == ["prop-w-1"] * 3
    assert log[1]["before"] == item("Cup") and log[1]["after"] == item("Blue Cup")
    assert "after" not in log[2] and "before" not in log[0]
    assert all(c["path"] == REL and c["by"] == "writer" for c in log)


def test_an_unchanged_write_logs_nothing(tmp_path):
    f = film.Film.create(tmp_path)
    f.writeText(REL, item("Cup"))
    f.writeText(REL, item("Cup"))

    assert len(lines(tmp_path)) == 1


def test_bookkeeping_and_the_script_are_not_logged(tmp_path):
    f = film.Film.create(tmp_path, "x\n")
    f.newId("prop")
    f.writeText("script.fountain", "y\n")
    f.saveIndex()

    assert lines(tmp_path) == []


def test_revert_an_authors_changes(tmp_path):
    f = film.Film.create(tmp_path)
    f.writeText(REL, item("Cup"), by="creator")
    f.writeText(REL, item("Agent Cup"), by="props-continuity-planner")
    f.writeText("bible/props/new/item.json", item("New"), by="props-continuity-planner")

    f.revert(f.changes(by="props-continuity-planner"), by="creator")

    assert (tmp_path / REL).read_text() == item("Cup")
    assert not (tmp_path / "bible/props/new/item.json").exists()
    assert [c.by for c in f.changes()][-2:] == ["creator", "creator"]
    assert len(f.changes(by="props-continuity-planner")) == 2


def test_each_line_is_a_change_message(tmp_path):
    f = film.Film.create(tmp_path)
    f.writeText(REL, item("Cup"))
    text = next((tmp_path / "history").glob("*.jsonl")).read_text()

    assert len(text.splitlines()) == 1
    assert mc.from_json(mc.Change, text.splitlines()[0]).path == REL


def test_a_broken_line_is_a_problem(tmp_path):
    f = film.Film.create(tmp_path)
    f.writeText(REL, item("Cup"))
    path = next((tmp_path / "history").glob("*.jsonl"))
    path.write_text(path.read_text() + "{\n")

    assert len(f.changes()) == 1
    assert f.problems[-1].what == "Change log"
