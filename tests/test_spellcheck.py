# spellcheck/pt-br/1: the spell checker in English or pt-BR
# (trelby/spellcheck.py); pt-BR needs the Docker image's hunspell-pt-br

import pytest

import tests.u as u
import trelby.config as config
import trelby.spellcheck as spellcheck

PTBR = """\
INT. SALA DE JANTAR - NOITE

Ana pega as xícaras e corre até a cozinha. Elas cantavam canções antigas.

ANA
Nós correríamos se pudéssemos, mas o açúcar acabou.
"""


def setup_module():
    u.init()


def unknown(text, lang):
    assert spellcheck.loadLanguage(lang) is None
    sp = u.loadString(text)
    sc = spellcheck.SpellChecker(sp, spellcheck.Dict(), lang)
    out = []

    while sc.findNext():
        out.append(sc.word)
        sc.col += len(sc.word)

    return out


def test_a_correct_ptbr_scene_has_no_unknown_word():
    assert unknown(PTBR, "pt-BR") == []


def test_a_misspelled_ptbr_word_is_found_and_suggested():
    assert unknown("Ana pega a xicara.\n", "pt-BR") == ["xicara"]
    assert spellcheck.suggest("pt-BR", "xicara", [])[0] == "xícara"


def test_english_is_unchanged():
    assert unknown("Ana takes the cup.\n", "en") == []
    assert "xícaras" in unknown(PTBR, "en")
    assert "cup" in spellcheck.suggest("en", "cupp", [])


def test_the_users_words_are_known_and_suggested_in_either_language():
    d = spellcheck.Dict()
    d.add("zorbak")
    sp = u.loadString("Zorbak anda.\n")

    for lang in ("en", "pt-BR"):
        spellcheck.loadLanguage(lang)

        assert spellcheck.SpellChecker(sp, d, lang).isKnown("Zorbak")
        assert "zorbak" in spellcheck.suggest(lang, "zorbac", [d])


def test_a_missing_dictionary_gives_the_message(monkeypatch):
    monkeypatch.setattr(spellcheck, "LANGUAGES", spellcheck.LANGUAGES + (("xx", "X", "xx_XX"),))
    err = spellcheck.loadLanguage("xx")

    assert "xx" in err and "hunspell-pt-br" in err


@pytest.mark.parametrize("lang", ["en", "pt-BR"])
def test_the_setting_round_trips(lang):
    c = config.ConfigGlobal()
    c.spellLanguage = lang
    d = config.ConfigGlobal()
    d.load(c.save())

    assert d.spellLanguage == lang


def test_an_old_config_or_a_bad_value_is_english():
    d = config.ConfigGlobal()
    d.load("SpellCheckerLanguage:klingon\n")

    assert d.spellLanguage == "en"
    assert config.ConfigGlobal().spellLanguage == "en"
