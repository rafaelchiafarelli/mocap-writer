# fountain-native/settings/1: a script's settings as a film record

import json
from pathlib import Path

import pytest

import tests.u as u
import trelby.film as film
import trelby.fountain as fountain
import trelby.screenplay as screenplay
import trelby.scriptsettings as scriptsettings
import trelby.util as util
import mocap_contracts as mc

CONTRACTS = Path(__file__).resolve().parents[1] / "third_party" / "mocap-contracts" / "fixtures" / "script-v1"

TEXT = "Title: A Film\nAuthor: Someone\n\nINT. ROOM - DAY #1#\n\nShe waits.\n"


def setup_module():
    u.init()


def load(text=TEXT):
    return u.loadString(text)


def test_the_defaults_are_the_contracts_fixture():
    sp = load("")
    text = scriptsettings.toJson(sp)

    assert text == (CONTRACTS / "settings" / "script-settings.json").read_text()


def changed(sp):
    sp.cfg.fontSize = 10
    sp.cfg.marginLeft = 30.5
    sp.cfg.pdfShowSceneNumbers = True
    sp.cfg.strMore = "(MAIS)"
    t = sp.cfg.getType(screenplay.ACTION)
    t.indent = 2
    t.screen.isItalic = True
    sp.headers.emptyLinesAfter = 2
    sp.headers.hdrs[0].text = "pág. ${PAGE}"
    sp.autoCompletion.types[screenplay.CHARACTER].items = ["ANA", "BIA"]
    sp.locations.locations = [["INT. ROOM - DAY", "INT. ROOM - NIGHT"]]
    sp.scDict.words = {"açúcar": None}
    sp.titles.pages[0][0].y = 80.5
    sp.titles.pages[0][0].size = 18


def test_settings_changed_saved_reopened_equal():
    sp = load()
    changed(sp)
    rec = scriptsettings.toJson(sp, sp.fountainSource.title)
    sp2 = load()
    problems = scriptsettings.apply(sp2, scriptsettings.fromJson(rec), sp2.fountainSource.title)

    assert problems == []
    assert scriptsettings.toJson(sp2, sp2.fountainSource.title) == rec
    assert sp2.cfg.getType(screenplay.ACTION).indent == 2 and sp2.scDict.words == {"açúcar": None}
    assert sp2.titles.pages[0][0].size == 18


def test_a_title_page_edited_elsewhere_opens_from_fountain():
    sp = load()
    changed(sp)
    rec = scriptsettings.fromJson(scriptsettings.toJson(sp, sp.fountainSource.title))
    sp2 = load(TEXT.replace("Someone", "Someone Else"))
    problems = scriptsettings.apply(sp2, rec, sp2.fountainSource.title)

    assert len(problems) == 1 and "title page" in problems[0]
    assert sp2.titles.pages[0][0].size != 18


def test_out_of_range_is_refused_not_clamped():
    sp = load()
    data = json.loads(scriptsettings.toJson(sp))
    data["page"]["font_size_pt"] = 99

    with pytest.raises(mc.ContractError, match="font_size_pt must be 4..72"):
        scriptsettings.fromJson(json.dumps(data))


def test_the_film_round_trip(tmp_path):
    sp = load()
    f = film.Film.create(tmp_path, fountain.generate(sp).text)
    changed(sp)
    sp.fountainSource = fountain.parse((tmp_path / "script.fountain").read_text())
    scriptsettings.saveFor(f, sp)
    before = (tmp_path / "script.fountain").read_text()

    g = film.Film.open(tmp_path)
    sp2 = fountain.load(g.readText("script.fountain"), sp.cfgGl)
    scriptsettings.loadFor(g, sp2)

    assert g.problems == []
    assert sp2.cfg.fontSize == 10
    assert (tmp_path / "script.fountain").read_text() == before
    assert [c.path for c in g.changes()] == ["settings/script-settings.json"]


def test_an_invalid_record_is_a_problem_and_the_script_keeps_the_defaults(tmp_path):
    sp = load()
    f = film.Film.create(tmp_path, fountain.generate(sp).text)
    (tmp_path / "settings").mkdir(exist_ok=True)
    (tmp_path / "settings/script-settings.json").write_text("{}")
    sp2 = load()
    scriptsettings.loadFor(film.Film.open(tmp_path), sp2)
    g = film.Film.open(tmp_path)
    scriptsettings.loadFor(g, sp2)

    assert [p.what for p in g.problems] == ["Script settings"]
    assert sp2.cfg.fontSize == 12


def test_no_record_keeps_the_defaults(tmp_path):
    sp = load()
    f = film.Film.create(tmp_path, fountain.generate(sp).text)
    scriptsettings.loadFor(f, sp)

    assert f.problems == [] and sp.cfg.fontSize == 12
