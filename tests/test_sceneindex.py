# preprod-link/contract/1: the scene index (trelby/sceneindex.py)

import mocap_contracts as mc

import tests.u as u
import trelby.bible as bible
import trelby.film as film
import trelby.sceneindex as sceneindex

SCRIPT = """\
INT. SALA DE JANTAR - NOITE #1#

ANA pega a XÍCARA AZUL. Bia olha.

ANA
Bom dia.

EXT. RUA - DIA #2#

Bia anda com uma CAIXA. Um TV toca.

BIA
Oi.

INT. COZINHA #3#

Nada.
"""


def setup_module():
    u.init()


def newBible(root):
    return bible.Bible(film.Film.create(root, SCRIPT))


def test_heading_parts():
    assert sceneindex.headingParts("INT. SALA DE JANTAR - NOITE") == ("INT.", "SALA DE JANTAR", "NOITE")
    assert sceneindex.headingParts("INT./EXT. CARRO - DIA") == ("INT./EXT.", "CARRO", "DIA")
    assert sceneindex.headingParts("COZINHA") == ("", "COZINHA", "")


def test_neutral_script_without_bible():
    idx = sceneindex.build(u.loadString(SCRIPT), None)
    s1, s2, s3 = idx.scenes

    assert [s.scene for s in idx.scenes] == ["1", "2", "3"]
    assert [s.order for s in idx.scenes] == [1, 2, 3]
    assert (s1.int_ext, s1.location, s1.time_of_day) == ("INT.", "SALA DE JANTAR", "NOITE")
    assert not s1.HasField("set_id")
    # ANA speaks; Bia is a speaker of the script named in Action
    assert [(c.name, c.speaks == sceneindex.ON) for c in s1.characters] == [
        ("ANA", True), ("BIA", False)]
    assert [p.word for p in s1.props] == ["XÍCARA AZUL"]
    assert [p.word for p in s2.props] == ["CAIXA", "TV"]
    assert s3.time_of_day == "" and s3.characters == [] and s3.props == []
    assert s1.first_line == 1 and s1.last_line < s2.first_line
    assert s1.first_page == 1


def test_links_give_ids_and_unknown_names_stay_as_written(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala de Jantar")
    b.link(sala, "1")
    ana = b.create("character", "Ana")
    cup = b.create("prop", "Xícara azul")
    idx = sceneindex.build(u.loadString(SCRIPT), b)
    s1 = idx.scenes[0]

    assert s1.set_id == sala.id
    assert s1.characters[0].id == ana.id
    assert not s1.characters[1].HasField("id")
    assert s1.props[0].id == cup.id
    assert not idx.scenes[1].props[0].HasField("id")


def test_not_props_are_left_out(tmp_path):
    b = newBible(tmp_path)
    b.notProps.append("TV")

    assert [p.word for p in sceneindex.build(u.loadString(SCRIPT), b).scenes[1].props] == ["CAIXA"]


def test_same_script_twice_gives_the_same_file_and_nothing_is_logged(tmp_path):
    b = newBible(tmp_path)
    n = len(b.film.changes())
    a = sceneindex.write(b.film, b, u.loadString(SCRIPT))
    c = sceneindex.write(b.film, b, u.loadString(SCRIPT))

    assert a == c
    assert (tmp_path / "bible" / "scene-index.json").read_text() == a
    assert mc.from_json(mc.SceneIndex, a).scenes[2].scene == "3"
    assert len(b.film.changes()) == n


def test_an_edit_changes_only_that_scenes_hash():
    a = sceneindex.build(u.loadString(SCRIPT), None)
    b = sceneindex.build(u.loadString(SCRIPT.replace("Oi.", "Olá.")), None)

    assert [x.text_hash == y.text_hash for x, y in zip(a.scenes, b.scenes)] == [True, False, True]
    assert a.script_hash != b.script_hash
