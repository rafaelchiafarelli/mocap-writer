# preprod-link/contract/2: the change set between two scene indexes
# (trelby/changeset.py)

import mocap_contracts as mc

import tests.u as u
import trelby.changeset as changeset
import trelby.sceneindex as sceneindex

BASE = """\
INT. SALA - NOITE #1#

ANA pega a CAIXA.

ANA
Oi.

EXT. RUA - DIA #2#

Nada.

INT. COZINHA - DIA #3#

Nada aqui.
"""


def setup_module():
    u.init()


def idx(text):
    return sceneindex.build(u.loadString(text), None)


def changes(old, new):
    cs = changeset.diff(idx(old) if old else None, idx(new), "2026-10-31T12:00:00Z")
    mc.to_json(cs)

    return [(mc.SceneChangeType.Name(c.type).removeprefix("SCENE_CHANGE_TYPE_"), c.scene,
             c.old_value, c.new_value) for c in cs.changes]


def test_identical_indexes_give_an_empty_change_set():
    cs = changeset.diff(idx(BASE), idx(BASE), "2026-10-31T12:00:00Z")

    assert list(cs.changes) == []
    assert cs.from_hash == cs.to_hash


def test_first_sync_reports_every_scene_added():
    cs = changeset.diff(None, idx(BASE), "2026-10-31T12:00:00Z")

    assert not cs.HasField("from_hash")
    assert [c.scene for c in cs.changes] == ["1", "2", "3"]


def test_scene_added_and_removed():
    new = BASE.replace("EXT. RUA - DIA #2#\n\nNada.\n\n", "") + "\nEXT. PRAIA - DIA #4#\n\nMar.\n"

    assert changes(BASE, new) == [
        ("SCENE_REMOVED", "2", "EXT. RUA - DIA", ""),
        ("SCENE_ADDED", "4", "", "EXT. PRAIA - DIA"),
    ]


def test_heading_changed_also_changes_the_text():
    assert changes(BASE, BASE.replace("RUA - DIA", "RUA - NOITE")) == [
        ("HEADING_CHANGED", "2", "EXT. RUA - DIA", "EXT. RUA - NOITE"),
        ("TEXT_CHANGED", "2", "", ""),
    ]


def test_text_changed():
    assert changes(BASE, BASE.replace("Nada aqui.", "Tudo aqui.")) == [("TEXT_CHANGED", "3", "", "")]


def test_character_entered_and_left():
    new = BASE.replace("ANA\nOi.", "BIA\nOi.").replace("ANA pega", "Ela pega")

    assert changes(BASE, new) == [
        ("TEXT_CHANGED", "1", "", ""),
        ("CHARACTER_ENTERED", "1", "", "BIA"),
        ("CHARACTER_LEFT", "1", "ANA", ""),
    ]


def test_prop_added_and_removed():
    new = BASE.replace("a CAIXA", "o FÓSFORO")

    assert changes(BASE, new)[1:] == [
        ("PROP_ADDED", "1", "", "FÓSFORO"),
        ("PROP_REMOVED", "1", "CAIXA", ""),
    ]


def test_moved_and_edited_scene_reports_both():
    s1, s2, s3 = BASE.split("\n\nEXT. RUA")[0], "EXT. RUA" + BASE.split("EXT. RUA")[1].split("\n\nINT. COZINHA")[0], "INT. COZINHA" + BASE.split("INT. COZINHA")[1]
    new = s3.replace("Nada aqui.", "Outra coisa.").rstrip("\n") + "\n\n" + s1 + "\n\n" + s2 + "\n"

    assert changes(BASE, new) == [
        ("SCENE_MOVED", "3", "3", "1"),
        ("TEXT_CHANGED", "3", "", ""),
    ]


def test_set_link_changed():
    a = idx(BASE)
    b = idx(BASE)
    b.scenes[0].set_id = "set-w-1"

    cs = changeset.diff(a, b, "2026-10-31T12:00:00Z")

    assert [(c.scene, c.new_value) for c in cs.changes] == [("1", "set-w-1")]
