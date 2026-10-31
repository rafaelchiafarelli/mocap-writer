# capitalized words in an Action line: by convention the props of the scene
# (editor-ux/typing/2). a prop is a run of consecutive fully capitalized
# words (film-bible/links/2, Rafael 2026-10-25): "XÍCARA AZUL" is one prop,
# not two. no wx, so film-bible uses it to create prop records.

import re

# a word: letters (accented letters included, digits and _ excluded),
# possibly joined by a hyphen or an apostrophe ("WALKIE-TALKIE", "O'BRIEN")
WORD_RE = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*")


# return the props of 'line' as a list of (start, end, run) tuples, 'start'
# and 'end' being str indexes into 'line' (end exclusive), in the order
# they appear. a run is fully capitalized words separated by spaces only:
# punctuation, a digit or a word not fully capitalized ends it. a
# one-letter word sits inside a run ("CAIXA E VELA") but never starts or
# ends one, and a run needs a word of two letters or more.
#
# 'typingAt' is the cursor's index in the line while the user types in
# it: a run that reaches the end of the line with the cursor after it is
# still being typed, and is not returned until something ends it.
def find_prop_words(line, typingAt=None):
    runs = []
    cur = []

    def close():
        while cur and len(cur[-1].group()) == 1:
            cur.pop()

        while cur and len(cur[0].group()) == 1:
            cur.pop(0)

        if cur:
            runs.append((cur[0].start(), cur[-1].end(), line[cur[0].start() : cur[-1].end()]))

        cur.clear()

    prevEnd = None

    for m in WORD_RE.finditer(line):
        w = m.group()
        caps = w.isupper()

        if cur and (not caps or line[prevEnd : m.start()].strip(" ") != ""):
            close()

        if caps:
            cur.append(m)

        prevEnd = m.end()

    close()

    if typingAt is not None and runs:
        start, end, run = runs[-1]

        if line[end:].strip() == "" and typingAt >= end:
            runs.pop()

    return runs
