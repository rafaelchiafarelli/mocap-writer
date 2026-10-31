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
