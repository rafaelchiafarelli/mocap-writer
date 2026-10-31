# import-to-film: an import that ends in a complete film (trelby/importfilm.py)

import tests.u as u
import trelby.film as film
import trelby.importfilm as importfilm


def setup_module():
    u.init()


def test_the_original_is_copied_into_a_source_part_added_on_first_use(tmp_path):
    f = film.Film.create(tmp_path / "f", "")
    src = tmp_path / "Roteiro.pdf"
    src.write_bytes(b"%PDF-1.4 neutral")

    assert importfilm.copySource(f, str(src)) == "source/Roteiro.pdf"
    assert (tmp_path / "f" / "source" / "Roteiro.pdf").read_bytes() == b"%PDF-1.4 neutral"

    g = film.Film.open(tmp_path / "f")

    assert g.part("source").path == "source/" and g.problems == []
    # a second copy uses the same part
    assert importfilm.copySource(g, str(src)) == "source/Roteiro.pdf"
    assert [p.name for p in film.Film.open(tmp_path / "f").index.parts].count("source") == 1


def test_a_copy_is_not_in_the_change_log(tmp_path):
    f = film.Film.create(tmp_path / "f", "")
    src = tmp_path / "a.fountain"
    src.write_text("INT. SALA - DIA\n")
    importfilm.copySource(f, str(src))

    assert f.changes() == []


SCRIPT = """\
INT. SALA DE JANTAR - NOITE #1#

ANA pega a XÍCARA AZUL.

ANA
Bom dia.

EXT. RUA - DIA #2#

BIA anda com a CAIXA.

BIA
Oi.
"""


def newBible(root):
    import trelby.bible as bible

    return bible.Bible(film.Film.create(root, SCRIPT))


def lines(sections):
    return {s.map: [(k, l[0] if k == "new" else (l[0].name, l[1])) for k, l in s.lines()]
            for s in sections}


def test_the_combined_plan_of_a_neutral_script(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala de Jantar")

    assert lines(importfilm.plan(b, u.loadString(SCRIPT))) == {
        "set": [("link", ("Sala de Jantar", "1")), ("new", "RUA")],
        "character": [("new", "ANA"), ("new", "BIA")],
        # BIA speaks, so the run is no prop
        "prop": [("new", "XÍCARA AZUL"), ("new", "CAIXA")],
    }


def test_create_makes_exactly_the_ticked_items_and_links(tmp_path):
    b = newBible(tmp_path)
    secs = importfilm.plan(b, u.loadString(SCRIPT))
    made = importfilm.apply(b, secs, {"set": [1], "character": [0], "prop": [1]}, notProps=True)

    assert {m: [it.name for it in its] for m, its in made.items()} == {
        "set": ["RUA"], "character": ["ANA"], "prop": ["CAIXA"]}
    assert sorted(b.scenes(made["character"][0])) == ["1"]
    assert b.notProps == ["XÍCARA AZUL"]


def test_cancel_writes_nothing(tmp_path):
    b = newBible(tmp_path)
    importfilm.plan(b, u.loadString(SCRIPT))

    assert b.items == {} and b.film.changes() == []


def test_into_an_open_film_new_items_have_no_scenes_and_nothing_is_linked(tmp_path):
    b = newBible(tmp_path)
    sala = b.create("set", "Sala de Jantar")
    secs = importfilm.plan(b, u.loadString(SCRIPT))
    made = importfilm.apply(b, secs, {"set": [0, 1], "character": [0, 1]}, linkScenes=False)

    assert [b.scenes(it) for it in made["set"] + made["character"]] == [set(), set(), set()]
    assert b.scenes(sala) == set()
