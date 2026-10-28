# spellcheck/study/1: measure one way of checking pt-BR words.
#
#   measure.py flat <word-list>      Trelby's own loadDict + suggestion loop
#                                    on a flat list (run with /opt/venv/bin/python,
#                                    cwd /app, so trelby imports)
#   measure.py hunspell|enchant|spylls   a Hunspell engine on pt_BR.dic/.aff
#
# Prints load time, memory, the words of the samples it does not know and
# the suggestions for TYPOS. Words are split like Trelby does
# (util.isWordBoundary: alphanumerics and the apostrophe, trelby/util.py:599-611).

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = [
    "/app/tests/fixtures/fountain/sample_ptbr.fountain",
    os.path.join(HERE, "sample_long_ptbr.txt"),
]
DIC = "/usr/share/hunspell/pt_BR"

# typo -> the word meant
TYPOS = {
    "caza": "casa",
    "voce": "você",
    "nao": "não",
    "padaira": "padaria",
    "geladiera": "geladeira",
    "chuvva": "chuva",
    "conseguiriamos": "conseguiríamos",
    "previzão": "previsão",
    "agradeseu": "agradeceu",
    "acrodado": "acordado",
    "biscoitso": "biscoitos",
    "exceçao": "exceção",
}


def rss_kb():
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1])


def words_of(text):
    out, cur = [], ""
    for c in text:
        if c == "'" or c.isalnum():
            cur += c
        else:
            if cur:
                out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def flat(path):
    sys.path.insert(0, "/app")
    import trelby.translations as translations

    translations.trelby_translations_load()
    import trelby.config  # noqa: F401  (import order: util needs config first)
    import trelby.misc as misc
    import trelby.spellcheck as spellcheck
    import trelby.util as util

    misc.init(False)
    util.init(False)

    # loadDict reads trelby/dict_en.dat by a fixed name; point it at the list
    orig = util.loadMaybeCompressedFile
    util.loadMaybeCompressedFile = lambda _f, frame: orig(path, frame)

    def load():
        return spellcheck.loadDict(None)

    def known(w):
        w = util.lower(w)
        return w in spellcheck.gdict or w.isdigit()

    # SpellCheckDlg.OnSuggest / tryWord without the user dictionaries
    # (trelby/spellcheckdlg.py:166-226)
    def suggest(word):
        word = util.lower(word)
        wl, wstart, d = len(word), word[:2], 500
        fifo = util.FIFO(5)
        for w in spellcheck.prefixDict.get(util.getWordPrefix(word), ()):
            if w.startswith(wstart) and abs(wl - len(w)) <= 3:
                d2 = spellcheck.lev(word, w)
                if d2 <= d:
                    fifo.add(w)
                    d = d2
        return fifo.get()

    return load, known, suggest


def hunspell_():
    import hunspell

    h = None

    def load():
        nonlocal h
        h = hunspell.HunSpell(DIC + ".dic", DIC + ".aff")
        return True

    return load, lambda w: h.spell(w), lambda w: h.suggest(w)[:5]


def enchant_():
    import enchant

    d = None

    def load():
        nonlocal d
        d = enchant.Dict("pt_BR")
        return d.provider.name

    return load, lambda w: d.check(w), lambda w: d.suggest(w)[:5]


def spylls_():
    from spylls.hunspell import Dictionary

    d = None

    def load():
        nonlocal d
        d = Dictionary.from_files(DIC)
        return True

    return load, lambda w: d.lookup(w), lambda w: list(d.suggest(w))[:5]


def main():
    mode = sys.argv[1]
    load, known, suggest = {
        "flat": lambda: flat(sys.argv[2]),
        "hunspell": hunspell_,
        "enchant": enchant_,
        "spylls": spylls_,
    }[mode]()

    r0 = rss_kb()
    t0 = time.perf_counter()
    res = load()
    t1 = time.perf_counter()
    print(f"load: {t1 - t0:.2f} s, +{(rss_kb() - r0) / 1024:.0f} MB RSS ({res})")

    words = []
    for s in SAMPLES:
        words += words_of(open(s, encoding="utf-8").read())
    uniq = sorted(set(words))
    t0 = time.perf_counter()
    unknown = [w for w in uniq if not known(w)]
    t1 = time.perf_counter()
    print(
        f"check: {len(words)} words, {len(uniq)} distinct, "
        f"{(t1 - t0) / len(uniq) * 1e6:.0f} µs/word"
    )
    print(f"unknown ({len(unknown)}): {' '.join(unknown)}")

    hits, total = 0, 0.0
    for typo, meant in TYPOS.items():
        t0 = time.perf_counter()
        sug = suggest(typo)
        dt = time.perf_counter() - t0
        total += dt
        ok = meant in [util_lower(s) for s in sug]
        hits += ok
        print(f"  {typo:16} {'OK ' if ok else '-- '} {dt * 1000:7.0f} ms  {sug}")
    print(
        f"suggest: {hits}/{len(TYPOS)} with the meant word in the top 5, "
        f"{total / len(TYPOS) * 1000:.0f} ms each on average"
    )


def util_lower(s):
    return s.lower()


if __name__ == "__main__":
    main()
