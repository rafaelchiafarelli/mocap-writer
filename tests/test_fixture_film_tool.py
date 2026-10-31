# tools/make_fixture_film.py: the neutral film root other repositories test with

import hashlib
import importlib.util
from pathlib import Path

import mocap_contracts as mc

import tests.u as u

TOOL = Path(__file__).resolve().parent.parent / "tools" / "make_fixture_film.py"


def setup_module():
    u.init()


def test_the_tool_builds_a_film_whose_index_matches_its_last_sync(tmp_path):
    spec = importlib.util.spec_from_file_location("make_fixture_film", TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    tool.main(tmp_path / "film")

    root = tmp_path / "film"
    index = root / "bible" / "scene-index.json"
    scenes = [s.scene for s in mc.from_json(mc.SceneIndex, index.read_text()).scenes]
    changes = sorted((root / "bible" / "sync").glob("*-changes.json"))

    assert scenes == ["1", "2", "2.A", "3"]
    assert len(changes) == 2
    last = mc.from_json(mc.ChangeSet, changes[-1].read_text())
    assert last.to_hash == hashlib.sha256(index.read_bytes()).hexdigest()
    assert len(list((root / "bible").glob("*/*/item.json"))) == 8
