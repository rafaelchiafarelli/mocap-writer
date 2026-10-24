# words written fully in capitals in an Action line: by convention the
# props of the scene (editor-ux/typing/2). no wx, so film-bible can reuse
# it to create prop records.

import re

# a run of two or more letters (accented letters included, digits and _
# excluded), not part of a longer run of letters.
WORD_RE = re.compile(r"(?<![^\W\d_])[^\W\d_]{2,}(?![^\W\d_])")


# return the capitalized words of 'line' as a list of (start, end, word)
# tuples, 'start' and 'end' being str indexes into 'line' (end exclusive),
# in the order they appear.
def find_prop_words(line):
    return [
        (m.start(), m.end(), m.group())
        for m in WORD_RE.finditer(line)
        if m.group().isupper()
    ]
