# fountain-native/scenes/5: moves and Renumber all rewrite the records
# that name scenes

import tests.u as u
import trelby.bible as bible
import trelby.film as film
import trelby.scenenumbers as scenenumbers
import trelby.screenplay as screenplay

SCRIPT = """\
INT. A - DAY #1#

Alpha.

INT. B - DAY #2#

Beta.

INT. C - DAY #3#

Gamma.
"""


def setup_module():
    u.init()


def heads(sp):
    return [(sp.lines[l].text, n) for l, n in scenenumbers.scenesOf(sp)]


def moveSceneToEnd(sp, num):
    # cut the scene numbered num and paste it at the end, as the user does
    # (tests/test_scenes_save.py, testMoveIsOmittedAndNewNumber)
    sc = scenenumbers.scenesOf(sp)
    k = [i for i, (_l, n) in enumerate(sc) if n == num][0]
    sp.line, sp.column = sc[k][0], 0
    sp.cmd("setMark")
    sp.line = sc[k + 1][0] - 1 if k + 1 < len(sc) else len(sp.lines) - 1
    sp.column = len(sp.lines[sp.line].text)
    cd = sp.getSelectedAsCD(True)
    sp.line = len(sp.lines) - 1
    sp.column = len(sp.lines[-1].text)
    sp.cmd("splitElement")
    sp.paste(cd.lines)


def test_a_moved_scene_is_detected_on_save():
    sp = u.loadString(SCRIPT)
    moveSceneToEnd(sp, "1")

    assert scenenumbers.prepareSave(sp) == []
    assert sp.sceneMoves == {"1": "4"}
    assert ("OMITTED", "1") in heads(sp)


def test_an_edited_scene_is_not_a_move():
    sp = u.loadString(SCRIPT)
    moveSceneToEnd(sp, "1")
    i = [n for n, l in enumerate(sp.lines) if l.text == "Alpha."][0]
    sp.lines[i].text = "Alpha, changed."
    scenenumbers.prepareSave(sp)

    assert sp.sceneMoves == {}


def test_renumber_all_maps_every_scene_and_composes_with_a_move():
    sp = u.loadString(SCRIPT)
    moveSceneToEnd(sp, "1")
    scenenumbers.prepareSave(sp)
    scenenumbers.renumberAll(sp)

    # B 2 -> 1, C 3 -> 2, A was 1, moved to 4, now 3
    assert sp.sceneMoves == {"2": "1", "3": "2", "1": "3"}


def test_undo_takes_the_pending_moves_back():
    sp = u.loadString(SCRIPT)
    scenenumbers.renumberAll(sp)

    assert sp.sceneMoves == {}  # 1, 2, 3 stay 1, 2, 3

    moveSceneToEnd(sp, "1")
    scenenumbers.prepareSave(sp)
    assert sp.sceneMoves == {"1": "4"}
    sp.cmd("undo")
    assert sp.sceneMoves == {}


def test_the_records_follow(tmp_path):
    b = bible.Bible(film.Film.create(tmp_path, SCRIPT))
    a = b.create("set", "A")
    b.link(a, "1")
    ana = b.create("character", "Ana")
    b.setValues(ana, "per_scene.emotional_state", ["calm"], "script-stated", "1", "writer", scene="1")
    b.link(ana, "2")
    coat = b.create("wardrobe", "Coat")
    b.link(coat, "1", ana.id)

    changed = b.renameScenes({"1": "2", "2": "3"})
    c = bible.Bible(film.Film.open(tmp_path))

    assert {it.id for it in changed} == {a.id, ana.id, coat.id}
    assert c.scenes(c.get(a.id)) == {"2"}
    assert c.scenes(c.get(ana.id)) == {"2", "3"}  # 1 -> 2 and 2 -> 3, not 1 -> 3
    assert c.get(coat.id).msg.links[0].scene == "2"
    assert all(ch.by == "writer" for ch in c.film.changes()[-3:])
