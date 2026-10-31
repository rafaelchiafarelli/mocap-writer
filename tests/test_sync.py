# preprod-link/sync/1: snapshot and diff (trelby/sync.py)

import mocap_contracts as mc

import tests.u as u
import trelby.bible as bible
import trelby.film as film
import trelby.sync as sync

SCRIPT = """\
INT. SALA - NOITE #1#

ANA pega a CAIXA.

EXT. RUA - DIA #2#

Nada.
"""


def setup_module():
    u.init()


def newBible(root):
    return bible.Bible(film.Film.create(root, SCRIPT))


def kinds(r):
    return [(mc.SceneChangeType.Name(c.type), c.scene) for c in r.changes.changes]


def test_first_run_reports_every_scene_added_and_writes_only_the_change_set(tmp_path):
    b = newBible(tmp_path)
    r = sync.run(b.film, b, u.loadString(SCRIPT), "2026-10-31T12:00:00Z")

    assert kinds(r) == [("SCENE_CHANGE_TYPE_SCENE_ADDED", "1"), ("SCENE_CHANGE_TYPE_SCENE_ADDED", "2")]
    assert r.rel == "bible/sync/20261031T120000Z-changes.json"
    assert mc.from_json(mc.ChangeSet, (tmp_path / r.rel).read_text()) == r.changes
    assert sync.lastIndex(b.film) is None
    assert not (tmp_path / "bible" / "scene-index.json").exists()


def test_accept_then_run_again_gives_an_empty_change_set(tmp_path):
    b = newBible(tmp_path)
    edited = SCRIPT.replace("Nada.", "Algo.")
    sync.accept(b.film, sync.run(b.film, b, u.loadString(SCRIPT)))
    r = sync.run(b.film, b, u.loadString(edited))

    assert kinds(r) == [("SCENE_CHANGE_TYPE_TEXT_CHANGED", "2")]

    sync.accept(b.film, r)

    assert kinds(sync.run(b.film, b, u.loadString(edited))) == []
    assert (tmp_path / "bible" / "scene-index.json").read_text() == mc.to_json(r.index)


def test_a_run_not_accepted_can_be_repeated(tmp_path):
    b = newBible(tmp_path)
    sync.accept(b.film, sync.run(b.film, b, u.loadString(SCRIPT)))
    edited = SCRIPT.replace("a CAIXA", "o FÓSFORO")
    a = sync.run(b.film, b, u.loadString(edited), "2026-10-31T12:00:00Z")
    c = sync.run(b.film, b, u.loadString(edited), "2026-10-31T12:05:00Z")

    assert list(a.changes.changes) == list(c.changes.changes)
    assert a.changes.from_hash == c.changes.from_hash


def test_sync_files_are_not_in_the_change_log_and_the_bible_still_opens(tmp_path):
    b = newBible(tmp_path)
    n = len(b.film.changes())
    sync.accept(b.film, sync.run(b.film, b, u.loadString(SCRIPT)))

    assert len(b.film.changes()) == n
    f = film.Film.open(tmp_path)
    assert bible.Bible(f).items == {} and f.problems == []


def test_change_lines_and_grouping_by_scene(tmp_path):
    b = newBible(tmp_path)
    sync.accept(b.film, sync.run(b.film, b, u.loadString(SCRIPT)))
    edited = SCRIPT.replace("RUA - DIA", "RUA - NOITE").replace("a CAIXA", "o FÓSFORO")
    r = sync.run(b.film, b, u.loadString(edited))
    groups = [(s, [sync.changeText(c) for c in cs]) for s, cs in sync.byScene(r.changes)]

    assert groups == [
        ("1", ["text changed", "prop added: FÓSFORO", "prop removed: CAIXA"]),
        ("2", ["heading changed: EXT. RUA - DIA → EXT. RUA - NOITE", "text changed"]),
    ]


def test_set_link_line_names_the_set(tmp_path):
    b = newBible(tmp_path)
    sync.accept(b.film, sync.run(b.film, b, u.loadString(SCRIPT)))
    sala = b.create("set", "Sala")
    b.link(sala, "1")
    r = sync.run(b.film, b, u.loadString(SCRIPT))
    names = lambda rid: b.get(rid).name

    assert [sync.changeText(c, names) for c in r.changes.changes] == ["set link changed: Sala"]


def withValues(tmp_path):
    b = newBible(tmp_path)
    ana = b.create("character", "Ana")
    b.setValues(ana, "identity.occupation", ["nurse"], "script-stated", "1", "creator")
    b.setValues(ana, "per_scene.emotional_state", ["calm"], "creator-approved",
                "creator 2026-10-31", "creator", scene="2")
    b.setValues(ana, "identity.age", ["34"], "creator-approved", "creator 2026-10-31", "creator")
    sync.accept(b.film, sync.run(b.film, b, u.loadString(SCRIPT)))

    return b, ana


def test_renamed_character_lists_the_values_its_scene_states(tmp_path):
    b, ana = withValues(tmp_path)
    r = sync.run(b.film, b, u.loadString(SCRIPT.replace("ANA pega", "BIA pega")))
    aff = sync.affected(b, r.changes)

    assert [(a.item.name, a.value.field, a.scene) for a in aff] == [
        ("Ana", "identity.occupation", "1")]
    assert sync.affectedText(aff[0]) == "needs review: Ana — Occupation: nurse"


def test_removed_scene_lists_its_per_scene_values(tmp_path):
    b, ana = withValues(tmp_path)
    r = sync.run(b.film, b, u.loadString(SCRIPT.split("EXT. RUA")[0]))

    assert [(a.value.field, a.scene) for a in sync.affected(b, r.changes)] == [
        ("per_scene.emotional_state", "2")]


def test_untouched_scenes_list_nothing_and_no_state_changes(tmp_path):
    b, ana = withValues(tmp_path)
    before = ana.msg.SerializeToString()
    r = sync.run(b.film, b, u.loadString(SCRIPT))

    assert sync.affected(b, r.changes) == []
    assert ana.msg.SerializeToString() == before
