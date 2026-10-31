# front-matter/record/1: the front matter record (trelby/frontmatter.py)

import mocap_contracts as mc

import tests.u as u
import trelby.film as film
import trelby.frontmatter as frontmatter


def setup_module():
    u.init()


def test_a_film_without_the_file_has_an_empty_front_matter(tmp_path):
    f = film.Film.create(tmp_path, "")
    fm = frontmatter.load(f)

    assert fm.title.title == "" and list(fm.title.co_authors) == []
    assert not frontmatter.isOn(fm.overview.include) and frontmatter.isOn(fm.overview.cast)
    assert f.problems == []


def test_save_load_round_trip_and_the_change_log(tmp_path):
    f = film.Film.create(tmp_path, "")
    fm = frontmatter.empty()
    fm.title.title = "A XÍCARA AZUL"
    fm.title.co_authors.extend(["Bia", "Cid"])
    fm.argument.include = frontmatter.ON
    fm.argument.text = "Ana perde a xícara.\n\nBia a encontra."

    assert frontmatter.save(f, fm)
    assert not frontmatter.save(f, fm)

    back = frontmatter.load(film.Film.open(tmp_path))

    assert back == fm
    assert [c.path for c in f.changes()] == ["settings/front-matter.json"]


def test_an_invalid_file_is_a_problem_not_a_crash(tmp_path):
    f = film.Film.create(tmp_path, "")
    (tmp_path / "settings").mkdir(exist_ok=True)
    (tmp_path / "settings" / "front-matter.json").write_text('{"title": 3}')
    g = film.Film.open(tmp_path)

    assert frontmatter.load(g) == frontmatter.empty()
    assert [p.where for p in g.problems] == ["settings/front-matter.json"]


def test_an_older_film_gets_the_part_on_first_save(tmp_path):
    f = film.Film.create(tmp_path, "")
    f.index.parts.remove(f.part("front-matter"))
    f.saveIndex()
    g = film.Film.open(tmp_path)
    frontmatter.save(g, frontmatter.empty())

    assert film.Film.open(tmp_path).part("front-matter").path == "settings/front-matter.json"


def filled():
    fm = frontmatter.empty()
    t = fm.title
    t.title, t.subtitle, t.episode = "A XÍCARA AZUL", "Um curta", "1"
    t.author = "Ana Exemplo"
    t.co_authors.extend(["Bia Exemplo"])
    t.email = "roteiro@example.com"

    return fm


def test_record_to_block():
    assert frontmatter.titleBlock(filled()) == (
        "Title: A XÍCARA AZUL\n"
        "Subtitle: Um curta\n"
        "Episode: 1\n"
        "Credit: Written by\n"
        "Authors:\n"
        "    Ana Exemplo\n"
        "    Bia Exemplo\n"
        "Contact: roteiro@example.com\n"
    )
    assert frontmatter.titleBlock(frontmatter.empty()) == ""


def test_block_to_record_round_trip():
    assert frontmatter.fromBlock(frontmatter.titleBlock(filled())) == filled().title
    t = frontmatter.fromBlock("Title:\n    THE CUP\n    a short\nAuthor: Ana & Bia\nContact:\n    Rua 1\n    a@b.c\n")

    assert (t.title, t.subtitle, t.author, list(t.co_authors), t.email) == (
        "THE CUP", "a short", "Ana", ["Bia"], "a@b.c")


SCRIPT = "Title: OLD TITLE\nAuthor: Someone\n\nINT. SALA - DIA #1#\n\nNada.\n"


def test_a_film_opened_with_a_block_and_no_record_keeps_it(tmp_path):
    import trelby.fountain as fountain

    f = film.Film.create(tmp_path, SCRIPT)
    sp = u.loadString(SCRIPT)
    fm = frontmatter.syncTitle(f, sp)

    assert (fm.title.title, fm.title.author) == ("OLD TITLE", "Someone")
    assert frontmatter.load(film.Film.open(tmp_path)).title.title == "OLD TITLE"
    assert fountain.generate(sp).text.startswith("Title: OLD TITLE\nCredit: Written by\nAuthor: Someone\n\nINT.")


def test_the_save_writes_the_block_from_the_record(tmp_path):
    import trelby.fountain as fountain

    f = film.Film.create(tmp_path, SCRIPT)
    frontmatter.save(f, filled())
    sp = u.loadString(SCRIPT)
    frontmatter.syncTitle(f, sp)
    text = fountain.generate(sp).text

    assert text.startswith(frontmatter.titleBlock(filled()) + "\nINT. SALA - DIA #1#")
    assert sp.titles.pages and sp.titles.pages[0][0].items == ["A XÍCARA AZUL"]
