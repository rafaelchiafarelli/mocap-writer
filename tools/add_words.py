#!/usr/bin/env python3
# add words to trelby/dict_en.dat, the spell checker's word list (UTF-8,
# one lower-case word per line, sorted, no duplicates):
#   tools/add_words.py word1 word2...

import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DICT = os.path.join(ROOT, "trelby", "dict_en.dat")


def main(args):
    if not args:
        sys.exit("usage: add_words.py word1 word2...")

    with open(DICT, encoding="utf-8") as f:
        words = set(f.read().splitlines())

    before = len(words)
    words.update(w.lower() for w in args)

    with open(DICT, "w", encoding="utf-8", newline="\n") as f:
        for w in sorted(words):
            f.write(w + "\n")

    print("%d word(s) added" % (len(words) - before))


if __name__ == "__main__":
    main(sys.argv[1:])
