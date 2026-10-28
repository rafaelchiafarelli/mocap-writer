# film-bible/links: the script's links to the bible (trelby/biblelinks.py)

import pytest

import tests.u as u
import trelby.bible as bible
import trelby.biblelinks as biblelinks
import trelby.film as film
import trelby.fountain as fountain
import trelby.scenenumbers as scenenumbers

SCRIPT = """\
INT. SALA DE JANTAR - NOITE #1#

ANA pega a XÍCARA AZUL e a CAIXA DE FÓSFORO.

ANA
Bom dia.

EXT. RUA - DIA #2#

Bia anda com a XÍCARAS AZUL. Um TV toca.

BIA
Oi.

INT. Sala de Jantar - DIA #3#

Nada.
"""


def setup_module():
    u.init()


def newBible(root):
    return bible.Bible(film.Film.create(root, SCRIPT))


def script():
    return u.loadString(SCRIPT)


def reopen(b):
    return bible.Bible(film.Film.open(b.film.root))


@pytest.mark.parametrize("heading, loc", [
    ("INT. SALA DE JANTAR - NOITE", "SALA DE JANTAR"),
    ("EXT. RUA - DIA", "RUA"),
    ("INT./EXT. CARRO - DIA", "CARRO"),
    ("I/E CARRO", "CARRO"),
    ("EST. CIDADE", "CIDADE"),
    ("COZINHA", "COZINHA"),
    ("INT. CASA - COZINHA - NOITE", "CASA - COZINHA"),
])
def test_location_of_a_heading(heading, loc):
    assert biblelinks.locationOf(heading) == loc


def test_a_new_location_is_offered_never_made(tmp_path):
    b = newBible(tmp_path)
    links, unknown = biblelinks.setPlan(b, script())

    assert links == [] and unknown == {"SALA DE JANTAR": ["1", "3"], "RUA": ["2"]}
    assert b.items == {}


def test_a_known_location_links_the_scene(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala de Jantar")
    links, unknown = biblelinks.setPlan(b, script())

    assert [(it.id, n) for it, n in links] == [(sala.id, "1"), (sala.id, "3")]
    assert unknown == {"RUA": ["2"]}

    biblelinks.applyLinks(b, links)

    assert biblelinks.setPlan(b, script())[0] == []
    assert b.scenes(sala) == {"1", "3"}


def test_creating_the_offered_sets_links_their_scenes(tmp_path):
    b = newBible(tmp_path)
    _links, unknown = biblelinks.setPlan(b, script())
    made = biblelinks.createSets(b, {"RUA": unknown["RUA"]})

    assert [(m.name, sorted(b.scenes(m))) for m in made] == [("RUA", ["2"])]


def test_renaming_the_set_keeps_the_link(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala de Jantar")
    biblelinks.applyLinks(b, biblelinks.setPlan(b, script())[0])
    b.rename(sala, "Dining Room")
    c = reopen(b)

    assert c.scenes(c.get(sala.id)) == {"1", "3"}


def test_an_alias_matches(tmp_path):
    b = newBible(tmp_path)
    rua = b.create("set", "Street")
    rua.msg.aliases.append("Rua")
    b.save(rua)

    assert [(it.id, n) for it, n in biblelinks.setPlan(b, script())[0]] == [(rua.id, "2")]


def test_a_set_with_no_scene_is_allowed(tmp_path):
    b = newBible(tmp_path)
    b.create("set", "Garage")

    assert reopen(b).get("set-w-1").msg.links == []


def test_the_scene_at_a_line_and_its_items(tmp_path):
    b = newBible(tmp_path)
    sp = script()
    sala = b.create("set", "Sala de Jantar")
    biblelinks.applyLinks(b, biblelinks.setPlan(b, sp)[0])

    assert [biblelinks.sceneAt(sp, i) for i in (0, 2, len(sp.lines) - 1)] == ["1", "1", "3"]
    assert biblelinks.itemsInScene(b, "3") == {"set": [sala]}
    assert biblelinks.itemsInScene(b, "2") == {}
