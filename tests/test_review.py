# preprod-link/review/1: the review queue (trelby/review.py)

import tests.u as u
import trelby.bible as bible
import trelby.film as film
import trelby.review as review
import trelby.sync as sync

SCRIPT = """\
INT. SALA - NOITE #1#

ANA pega a CAIXA.

EXT. RUA - DIA #2#

Nada.
"""


def setup_module():
    u.init()


def setup(tmp_path):
    b = bible.Bible(film.Film.create(tmp_path, SCRIPT))
    ana = b.create("character", "Ana")
    b.link(ana, "1")
    b.link(ana, "2")
    b.setValues(ana, "identity.occupation", ["nurse"], "creator-approved", "creator 2026-10-30", "creator")
    b.setValues(ana, "identity.occupation", ["doctor"], "proposal", "1", "props-continuity-planner")
    b.setValues(ana, "per_scene.emotional_state", ["angry"], "proposal", "2",
                "props-continuity-planner", scene="2")
    b.setValues(ana, "identity.age", [("34", "year")], "proposal", "1", "props-continuity-planner")

    return b, ana


def rows(b, changes=None):
    return [(e.scene, e.item.name, e.value.field, review.valueText(e.value), e.why)
            for e in review.queue(b, changes)]


def test_queue_groups_by_scene_with_item_level_values_last(tmp_path):
    b, ana = setup(tmp_path)

    assert rows(b) == [
        ("2", "Ana", "per_scene.emotional_state", "angry", "proposal"),
        (None, "Ana", "identity.age", "34 year", "proposal"),
        (None, "Ana", "identity.occupation", "doctor", "proposal"),
    ]
    assert review.appliesTo(b, review.queue(b)[1]) == ["1", "2"]


def test_batch_approve_keeps_sources_and_writes_each_item_once(tmp_path):
    b, ana = setup(tmp_path)
    n = len(b.film.changes())
    review.approve(b, review.queue(b))
    ana = bible.Bible(film.Film.open(tmp_path)).get(ana.id)

    assert rows(bible.Bible(film.Film.open(tmp_path))) == []
    assert {(v.field, bible.stateName(v.state), v.source) for v in ana.msg.values} >= {
        ("identity.age", "creator-approved", "1"),
        ("per_scene.emotional_state", "creator-approved", "2")}
    assert len(b.film.changes()) == n + 1


def test_reject_of_a_proposal_with_nothing_before_removes_it(tmp_path):
    b, ana = setup(tmp_path)
    review.reject(b, [e for e in review.queue(b) if e.value.field == "identity.age"])

    assert [v for v in bible.Bible(film.Film.open(tmp_path)).get(ana.id).msg.values
            if v.field == "identity.age"] == []


def test_reject_removes_the_proposal_and_leaves_the_previous_value(tmp_path):
    b, ana = setup(tmp_path)
    occ = [e for e in review.queue(b) if e.value.field == "identity.occupation"]
    review.reject(b, occ)
    ana = bible.Bible(film.Film.open(tmp_path)).get(ana.id)

    assert [(v.text, bible.stateName(v.state)) for v in ana.msg.values
            if v.field == "identity.occupation"] == [("nurse", "creator-approved")]


def test_a_per_scene_override_is_shown_under_its_scene_only(tmp_path):
    b, ana = setup(tmp_path)

    assert [e.scene for e in review.queue(b) if e.value.field.startswith("per_scene")] == ["2"]


def test_edit_makes_it_the_creators(tmp_path):
    b, ana = setup(tmp_path)
    e = [e for e in review.queue(b) if e.value.field == "identity.age"][0]
    review.edit(b, e, "35")
    v = [v for v in bible.Bible(film.Film.open(tmp_path)).get(ana.id).msg.values
         if v.field == "identity.age"][0]

    assert (v.number, bible.stateName(v.state), v.by) == ("35", "creator-approved", "creator")


def test_needs_review_values_come_from_the_latest_sync(tmp_path):
    b, ana = setup(tmp_path)
    review.approve(b, review.queue(b))
    sync.accept(b.film, sync.run(b.film, b, u.loadString(SCRIPT)))
    sync.run(b.film, b, u.loadString(SCRIPT.replace("Nada.", "Algo.")))
    changes = review.latestChanges(b.film)

    assert rows(b, changes) == [
        ("2", "Ana", "per_scene.emotional_state", "angry", "needs review")]
