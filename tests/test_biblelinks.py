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


def test_props_are_runs_offered_never_made(tmp_path):
    b = newBible(tmp_path)
    links, new = biblelinks.propPlan(b, script())

    # ANA and BIA speak, so they are characters, not props; XÍCARAS is
    # the plural of XÍCARA
    assert links == []
    assert new == {"XÍCARA AZUL": ["1", "2"], "CAIXA DE FÓSFORO": ["1"], "TV": ["2"]}
    assert b.items == {}


def test_a_known_prop_links_its_scenes(tmp_path):
    b = newBible(tmp_path)
    cup = b.create("prop", "Xícara Azul")
    links, new = biblelinks.propPlan(b, script())

    assert [(it.id, n) for it, n in links] == [(cup.id, "1"), (cup.id, "2")]
    assert "XÍCARA AZUL" not in new


def test_made_props_link_their_scenes(tmp_path):
    b = newBible(tmp_path)
    (made,) = biblelinks.createProps(b, {"TV": ["2"]})

    assert (made.name, b.scenes(made)) == ("TV", {"2"})


def test_not_a_prop_is_remembered_for_the_film(tmp_path):
    b = newBible(tmp_path)
    biblelinks.markNotProps(b, ["TV"])
    c = reopen(b)

    assert "TV" not in biblelinks.propPlan(c, script())[1]


def test_a_bible_character_is_not_a_prop(tmp_path):
    b = newBible(tmp_path)
    b.create("character", "Caixa de Fósforo")

    assert "CAIXA DE FÓSFORO" not in biblelinks.propPlan(b, script())[1]


def test_the_run_being_typed_is_not_offered(tmp_path):
    sp = u.loadString("INT. ROOM #1#\n\nShe takes the BLUE CU\n")
    line = [i for i, l in enumerate(sp.lines) if "BLUE" in l.text][0]
    b = newBible(tmp_path)

    assert biblelinks.propPlan(b, sp, line, len(sp.lines[line].text))[1] == {}
    assert biblelinks.propPlan(b, sp)[1] == {"BLUE CU": ["1"]}


def test_wardrobe_links_and_gaps(tmp_path):
    import trelby.bibleedit as bibleedit

    b = newBible(tmp_path)
    ana = b.create("character", "Ana")
    bia = b.create("character", "Bia")
    coat = b.create("wardrobe", "Coat")
    sp = script()

    assert biblelinks.charactersByScene(b, sp) == {"1": {ana.id}, "2": {bia.id}}
    assert biblelinks.wardrobeGaps(b, sp) == [("1", ana.id), ("2", bia.id)]

    biblelinks.linkWardrobe(b, coat, ana, "1")

    assert biblelinks.wardrobeGaps(b, sp) == [("2", bia.id)]
    assert bibleedit.wornText(b, coat) == "Ana in 1"

    bibleedit.setWorn(b, coat, ana, ["2"])

    assert bibleedit.wornScenes(reopen(b).get(coat.id), ana.id) == ["2"]

    biblelinks.unlinkWardrobe(b, coat, ana, "2")

    assert reopen(b).get(coat.id).msg.links == []


def test_wardrobe_with_no_character_is_allowed(tmp_path):
    b = newBible(tmp_path)
    b.create("wardrobe", "Spare Coat")

    assert reopen(b).get("wardrobe-w-1").msg.links == []


def roomWithFiles(b, tmp_path):
    room = b.create("set", "Room")
    table = b.create("set", "Table", parent=room)
    ana = b.create("character", "Ana")
    (tmp_path / "plan.png").write_bytes(b"png")
    b.setValues(room, "size.floor_plan", [b.addFile(room, tmp_path / "plan.png", "plans")],
                "creator-approved", "decision", "creator")
    b.setValues(room, "continuity.changes", ["broken"], "script-stated", "1", "writer", scene="1")
    b.setValues(table, "dressing.state", ["dirty"], "script-stated", "1", "writer")
    b.link(room, "1")
    b.link(room, "3")

    return room, table, ana


def test_copy_keeps_files_and_children_with_new_ids(tmp_path):
    b = newBible(tmp_path / "f")
    room, table, _ana = roomWithFiles(b, tmp_path)
    copy = biblelinks.copyItem(b, room, b, None, name="Room copy")
    c = reopen(b)
    got = c.get(copy.id)
    (kid,) = c.children("set", copy.id)

    assert copy.id not in (room.id, table.id) and kid.id not in (room.id, table.id)
    assert got.name == "Room copy" and got.msg.links == []
    assert (tmp_path / "f" / got.folder / "plans" / "plan.png").read_bytes() == b"png"
    assert c.film.problems == []
    assert [v.field for v in got.msg.values] == ["size.floor_plan"]
    assert c.values(kid, "dressing.state")[0].text == "dirty"
    assert c.get(room.id).msg.links  # the original keeps its scenes


def test_cross_film_copy_drops_the_scene_links(tmp_path):
    a = newBible(tmp_path / "a")
    room, _table, _ana = roomWithFiles(a, tmp_path)
    b = newBible(tmp_path / "b")
    b.create("set", "Other")
    copy = biblelinks.copyItem(a, room, b)
    c = reopen(b)

    assert copy.id == "set-w-2"
    assert c.get(copy.id).msg.links == [] and c.scenes(c.get(copy.id)) == set()
    assert len(c.children("set", copy.id)) == 1
    assert (tmp_path / "b" / c.get(copy.id).folder / "plans" / "plan.png").exists()


def test_cross_film_copy_drops_links_to_other_items(tmp_path):
    a = newBible(tmp_path / "a")
    cup = a.create("prop", "Cup")
    ana = a.create("character", "Ana")
    a.setValues(cup, "ownership.owner", [ana.id], "creator-approved", "x", "creator")
    b = newBible(tmp_path / "b")

    assert biblelinks.copyItem(a, cup, b).msg.values == []
    assert biblelinks.copyItem(a, cup, a).msg.values[0].text == ana.id


def test_the_warning_lists_the_scenes(tmp_path):
    b = newBible(tmp_path / "f")
    room, _t, _a = roomWithFiles(b, tmp_path)

    assert biblelinks.usedIn(b, room) == ["1", "3"]


@pytest.mark.parametrize("text, name", [
    ("ANA", "ANA"), ("ANA (V.O.)", "ANA"), ("ANA (CONT'D)", "ANA"), ("ANA ^", "ANA"),
    ("ANA (O.S.) ^", "ANA"), ("DR. SILVA", "DR. SILVA"),
])
def test_the_speaker_of_a_character_element(text, name):
    assert biblelinks.speaker(text) == name


CAST = """\
INT. SALA - NOITE #1#

ANA
Oi.

BIA (V.O.)
Oi.

EXT. RUA - DIA #2#

ANA (CONT'D)
Tchau.
"""


def test_characters_are_offered_never_made(tmp_path):
    b = newBible(tmp_path)
    links, new = biblelinks.characterPlan(b, u.loadString(CAST))

    assert links == [] and new == {"ANA": ["1", "2"], "BIA": ["1"]}
    assert b.items == {}


def test_a_known_character_or_alias_is_linked(tmp_path):
    b = newBible(tmp_path)
    ana = b.create("character", "Ana")
    bia = b.create("character", "Beatriz")
    bia.msg.aliases.append("Bia")
    b.save(bia)
    links, new = biblelinks.characterPlan(b, u.loadString(CAST))

    assert [(it.id, n) for it, n in links] == [(ana.id, "1"), (bia.id, "1"), (ana.id, "2")]
    assert new == {}

    biblelinks.applyLinks(b, links)

    assert biblelinks.characterPlan(b, u.loadString(CAST)) == ([], {})


def test_made_characters_are_linked_to_their_scenes(tmp_path):
    b = newBible(tmp_path)
    (ana,) = biblelinks.createCharacters(b, {"ANA": ["1", "2"]})

    assert (ana.name, reopen(b).scenes(reopen(b).get(ana.id))) == ("ANA", {"1", "2"})
