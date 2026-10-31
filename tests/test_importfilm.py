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
