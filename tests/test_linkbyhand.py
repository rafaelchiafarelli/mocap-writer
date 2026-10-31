# film-bible/links/6: scenes linked by hand (trelby/bibleedit.py)

import tests.u as u
import trelby.bible as bible
import trelby.bibleedit as bibleedit
import trelby.film as film

SCRIPT = """\
INT. SALA - NOITE #1#

Nada.

EXT. RUA - DIA #2#

Nada.

INT. QUARTO - DIA #3#

Nada.
"""


def setup_module():
    u.init()


def newBible(root):
    return bible.Bible(film.Film.create(root, SCRIPT))


def reopen(b):
    return bible.Bible(film.Film.open(b.film.root))


def test_scene_labels_have_number_and_heading_and_keep_a_gone_scene(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala")
    b.link(sala, "9")

    assert bibleedit.sceneLabels(b, sala, u.loadString(SCRIPT)) == [
        ("1", "1 — INT. SALA - NOITE"),
        ("2", "2 — EXT. RUA - DIA"),
        ("3", "3 — INT. QUARTO - DIA"),
        ("9", "9"),
    ]


def test_set_scenes_adds_and_removes_the_difference_only(tmp_path):
    b = newBible(tmp_path)
    ana = b.create("character", "Ana")
    b.link(ana, "1")
    b.link(ana, "2")
    bibleedit.commit(b, ana, "per_scene.emotional_state", "angry", scene="2")
    n = len(b.film.changes())

    assert bibleedit.setScenes(b, ana, ["1", "3"])
    assert len(b.film.changes()) == n + 1

    ana = reopen(b).get(ana.id)

    assert sorted(bibleedit.linkedScenes(ana)) == ["1", "3"]
    # the per-scene value of scene 2 stays
    assert bibleedit.text(b, ana, "per_scene.emotional_state", "2") == "angry"


def test_nothing_written_when_nothing_changed(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala")
    b.link(sala, "1")
    n = len(b.film.changes())

    assert not bibleedit.setScenes(b, sala, ["1"])
    assert bibleedit.setSceneItems(b, "1", [sala.id]) == []
    assert len(b.film.changes()) == n


def test_scene_side_links_and_unlinks_all_three_maps(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala")
    canto = b.create("set", "Canto", parent=sala)
    ana = b.create("character", "Ana")
    cx = b.create("prop", "Caixa")
    b.link(ana, "2")

    assert [(it.name, d) for it, d in bibleedit.sceneItemChoices(b)] == [
        ("Sala", 0), ("Canto", 1), ("Ana", 0), ("Caixa", 0)]

    changed = bibleedit.setSceneItems(b, "2", [canto.id, cx.id])

    assert {it.id for it in changed} == {canto.id, cx.id, ana.id}

    b = reopen(b)

    assert bibleedit.sceneItems(b, "2") == {canto.id, cx.id}
    assert bibleedit.linkedScenes(b.get(ana.id)) == []


def test_scene_side_leaves_wardrobe_alone(tmp_path):
    b = newBible(tmp_path)
    ana = b.create("character", "Ana")
    coat = b.create("wardrobe", "Casaco")
    bibleedit.setWorn(b, coat, ana, ["2"])

    bibleedit.setSceneItems(b, "2", [])

    assert bibleedit.wornScenes(reopen(b).get(coat.id), ana.id) == ["2"]


def test_set_scenes_keeps_wardrobe_character_links(tmp_path):
    b = newBible(tmp_path)
    ana = b.create("character", "Ana")
    coat = b.create("wardrobe", "Casaco")
    bibleedit.setWorn(b, coat, ana, ["2"])
    bibleedit.setScenes(b, coat, ["1"])

    coat = reopen(b).get(coat.id)

    assert bibleedit.wornScenes(coat, ana.id) == ["2"]
    assert bibleedit.linkedScenes(coat) == ["1"]
