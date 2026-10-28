# file-format/layout/1: a film root (trelby/film.py)

import json
import shutil
from pathlib import Path

import pytest

import tests.u as u
import trelby.film as film
import mocap_contracts as mc

CONTRACTS = Path(__file__).resolve().parents[1] / "third_party" / "mocap-contracts" / "fixtures" / "film-v1"


def setup_module():
    u.init()


def test_new_film_gets_a_valid_film_json(tmp_path):
    f = film.Film.create(tmp_path / "f", "INT. ROOM - DAY\n")
    index = mc.from_json(mc.Film, (tmp_path / "f" / "film.json").read_text())

    assert [p.name for p in index.parts] == [n for n, _p in film.DEFAULT_PARTS]
    assert index.origin.program == "mocap-writer"
    assert (tmp_path / "f" / "script.fountain").read_text() == "INT. ROOM - DAY\n"
    assert (tmp_path / "f" / "bible").is_dir()
    assert film.Film.open(f.root).problems == []


def test_create_refuses_an_existing_film(tmp_path):
    film.Film.create(tmp_path)

    with pytest.raises(film.FilmError):
        film.Film.create(tmp_path)


def test_ids_count_per_kind_and_are_saved_first(tmp_path):
    f = film.Film.create(tmp_path)

    assert [f.newId("character"), f.newId("character"), f.newId("prop")] == [
        "character-w-1", "character-w-2", "prop-w-1"]
    assert json.loads((tmp_path / "ids" / "w.json").read_text()) == {
        "next": {"character": 3, "prop": 2}}
    assert film.Film.open(tmp_path).newId("character") == "character-w-3"


def test_two_spaces_never_collide(tmp_path):
    f = film.Film.create(tmp_path)
    f.addSpace("pcp", "props-continuity-planner", "proposals/props-continuity-planner/")
    agent = film.Film.open(tmp_path, owner="props-continuity-planner")

    ids = {f.newId("prop") for _i in range(3)} | {agent.newId("prop") for _i in range(3)}

    assert len(ids) == 6
    assert agent.newId("proposal") == "proposal-pcp-1"


def test_a_part_written_by_another_owner_is_refused(tmp_path):
    f = film.Film.create(tmp_path)
    f.addSpace("pcp", "props-continuity-planner", "proposals/props-continuity-planner/")
    agent = film.Film.open(tmp_path, owner="props-continuity-planner")

    with pytest.raises(film.OwnerError):
        agent.writeText("bible/props/x/item.json", "{}")

    with pytest.raises(film.OwnerError):
        agent.writeText("film.json", "{}")

    with pytest.raises(film.OwnerError):
        f.writeText("proposals/props-continuity-planner/a.json", "{}")

    with pytest.raises(film.OwnerError):
        f.writeText("analysis/brief.md", "x")

    agent.writeText("proposals/props-continuity-planner/a.json", "{}")
    agent.newId("prop")

    with pytest.raises(film.OwnerError):
        agent.writeText("ids/w.json", "{}")


def test_ownership_is_a_prefix_check_by_segment(tmp_path):
    f = film.Film.create(tmp_path)

    assert f.ownerOf("bible/sets/a/item.json") == "writer"
    assert f.ownerOf("bible-old/x") is None
    assert f.partOf("settings/script-settings.json").name == "settings"


def test_an_invalid_film_json_names_the_broken_field(tmp_path):
    for name, case in json.loads((CONTRACTS / "invalid" / "expected.json").read_text()).items():
        if case["message"] != "Film":
            continue

        shutil.copy(CONTRACTS / "invalid" / name, tmp_path / "film.json")

        with pytest.raises(film.FilmError) as e:
            film.Film.open(tmp_path)

        assert case["error"] in str(e.value), name


def test_no_film_json_stops_the_open_with_a_message(tmp_path):
    with pytest.raises(film.FilmError, match="film.json is missing"):
        film.Film.open(tmp_path)


def test_a_film_with_a_part_and_a_file_deleted_opens_and_lists_both(tmp_path):
    f = film.Film.create(tmp_path, "x\n")
    (tmp_path / "script.fountain").unlink()
    shutil.rmtree(tmp_path / "annotations")
    (tmp_path / "ids" / "w.json").write_text("{")

    g = film.Film.open(tmp_path)

    assert [p.where for p in g.problems] == ["script.fountain", "annotations/", "ids/w.json"]
    assert g.part("bible") is not None


def test_a_lost_writer_counter_never_reuses_ids(tmp_path):
    film.Film.create(tmp_path)
    (tmp_path / "ids" / "w.json").unlink()
    g = film.Film.open(tmp_path)

    assert "ids/w.json" in [p.where for p in g.problems]

    with pytest.raises(film.FilmError):
        g.newId("prop")


def test_the_contracts_fixture_opens(tmp_path):
    shutil.copytree(CONTRACTS, tmp_path / "f", ignore=shutil.ignore_patterns("invalid"))
    f = film.Film.open(tmp_path / "f")

    assert {p.where for p in f.problems} == {
        "script.fountain", "bible/", "annotations/",
        "proposals/props-continuity-planner/", "history/"}


def test_an_agent_space_rule_is_checked_before_writing(tmp_path):
    f = film.Film.create(tmp_path)

    with pytest.raises(mc.ContractError):
        f.addSpace("BAD", "x")

    assert [s.code for s in film.Film.open(tmp_path).index.spaces] == ["w"]
