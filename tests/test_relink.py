# file-format/layout/3: missing files, search and relink (trelby/relink.py)

import shutil

import pytest

import tests.u as u
import trelby.film as film
import trelby.relink as relink


def setup_module():
    u.init()


# a neutral film whose script and folder parts were moved into archive/
def movedFilm(root):
    film.Film.create(root, "INT. ROOM - DAY\n")
    (root / "bible" / "props").mkdir()
    (root / "archive").mkdir()

    for name in ("script.fountain", "bible", "annotations"):
        shutil.move(root / name, root / "archive" / name)

    return film.Film.open(root)


def refs(f):
    return [p.ref for p in f.problems if p.ref]


def test_moved_parts_are_listed_with_refs(tmp_path):
    f = movedFilm(tmp_path)

    assert [(r.rel, r.kind) for r in refs(f)] == [
        ("script.fountain", "fountain"), ("bible/", "folder"), ("annotations/", "folder")]


def test_one_found_file_gives_the_pattern_for_the_rest(tmp_path):
    f = movedFilm(tmp_path)
    script, *others = refs(f)
    before = (tmp_path / "film.json").read_text()

    rel, why = relink.check(tmp_path, script, tmp_path / "archive" / "script.fountain")
    pat = relink.pattern(script.rel, rel)
    found = relink.suggest(tmp_path, pat, others)

    assert (rel, why, pat) == ("archive/script.fountain", None, ("", "archive"))
    assert [n for _r, n in found] == ["archive/bible/", "archive/annotations/"]
    assert (tmp_path / "film.json").read_text() == before

    script.apply(rel)

    for r, n in found:
        r.apply(n)

    assert film.Film.open(tmp_path).problems == []


def test_skip_keeps_the_file_listed(tmp_path):
    movedFilm(tmp_path)

    assert len(refs(film.Film.open(tmp_path))) == 3


def test_a_file_of_the_wrong_kind_is_refused(tmp_path):
    f = movedFilm(tmp_path)
    (tmp_path / "notes.txt").write_text("x")
    script, bible, _a = refs(f)

    assert relink.check(tmp_path, script, tmp_path / "notes.txt")[0] is None
    assert relink.check(tmp_path, bible, tmp_path / "notes.txt")[0] is None
    assert relink.check(tmp_path, bible, tmp_path / "archive" / "bible") == ("archive/bible/", None)


def test_a_file_outside_the_film_is_refused(tmp_path):
    f = movedFilm(tmp_path / "f")
    (tmp_path / "other.fountain").write_text("x")
    rel, why = relink.check(tmp_path / "f", refs(f)[0], tmp_path / "other.fountain")

    assert rel is None and "inside the film folder" in why


@pytest.mark.parametrize("old, new, pat", [
    ("a/b/x.png", "c/b/x.png", ("a", "c")),
    ("x.png", "photos/x.png", ("", "photos")),
    ("a/x.png", "b/y.png", ("a", "b")),
    ("bible/", "old/bible/", ("", "old")),
])
def test_pattern(old, new, pat):
    assert relink.pattern(old, new) == pat


def test_apply_pattern():
    assert relink.applyPattern(("a", "c"), "a/d/y.png") == "c/d/y.png"
    assert relink.applyPattern(("a", "c"), "b/y.png") is None
    assert relink.applyPattern(("", "old"), "bible/") == "old/bible/"


# the warning's title and text follow what it lists (bugs/editor/21)
def test_warning_text_tells_notices_from_missing_files(tmp_path):
    f = movedFilm(tmp_path)
    missing = [p for p in f.problems if p.ref]
    notice = film.Problem("Script settings", "settings/script-settings.json", "The title page was edited outside the writer.")

    title, intro = relink.warningText(missing)
    assert title == "Missing files" and "nothing to search for" not in intro

    title, intro = relink.warningText([notice])
    assert title == "Film notices" and "no file is missing" in intro

    title, intro = relink.warningText(missing + [notice])
    assert title == "Missing files" and "nothing to search for" in intro
