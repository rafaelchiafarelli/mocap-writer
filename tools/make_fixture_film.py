"""Build a neutral film root with the writer's own code, for other
repositories' tests (mocap-preprod's tests/fixtures/film/).

The film is made the way a creator would make it: a script, bible items
with values and scene links, the front matter, two annotations, then a
sync accepted on the first draft and on an edited one. No film material.

    python3 tools/make_fixture_film.py <empty-dir>

Run from the repository root, in the writer's image (docker/), with the
root on PYTHONPATH.
"""

import sys
from pathlib import Path

import trelby.translations as translations

translations.trelby_translations_load()

import trelby.annotations as annotations  # noqa: E402
import trelby.bible as bible  # noqa: E402
import trelby.config as config  # noqa: E402
import trelby.film as film  # noqa: E402
import trelby.fountain as fountain  # noqa: E402
import trelby.frontmatter as frontmatter  # noqa: E402
import trelby.misc as misc  # noqa: E402
import trelby.sync as sync  # noqa: E402
import trelby.util as util  # noqa: E402

SCRIPT = """\
INT. KITCHEN - NIGHT #1#

ANA fills the BLUE CUP and sets it on the table.

ANA
It's cold again.

MARCO enters, shaking off the rain.

MARCO
The bus didn't come.

EXT. STREET - DAY #2#

ANA walks under an UMBRELLA, the LETTER in her hand.

INT. KITCHEN - DAY #3#

MARCO washes the BLUE CUP.
"""

# the second draft: scene 2.A added, scene 3 rewritten with a new prop word
EDITED = SCRIPT.replace(
    "INT. KITCHEN - DAY #3#\n\nMARCO washes the BLUE CUP.\n",
    "INT. BUS - DAY #2.A#\n\nANA sits by the window. The LETTER is open on her lap.\n\n"
    "INT. KITCHEN - DAY #3#\n\nMARCO dries the BLUE CUP and finds the KEY under it.\n",
)


def load(text):
    return fountain.load(text, config.ConfigGlobal())


def main(root):
    misc.init(False)
    util.init(False)

    f = film.Film.create(root, SCRIPT)
    b = bible.Bible(f)

    kitchen = b.create("set", "Kitchen")
    street = b.create("set", "Street")
    ana = b.create("character", "Ana")
    marco = b.create("character", "Marco")
    cup = b.create("prop", "Blue Cup")
    letter = b.create("prop", "Letter")
    umbrella = b.create("prop", "Umbrella")
    coat = b.create("wardrobe", "Raincoat")

    b.setValues(kitchen, "space.int_ext", ["interior"], "script-stated", "1", "writer")
    b.setValues(kitchen, "light.natural", ["window"], "tbd", "1", "creator",
                revisit="before the set layout")
    b.setValues(street, "space.int_ext", ["exterior"], "script-stated", "2", "writer")
    b.setValues(ana, "identity.age", [("34", "year")], "creator-approved", "decision", "creator")
    b.setValues(marco, "identity.occupation", ["baker"], "creator-approved", "decision", "creator")
    b.setValues(cup, "look.color", ["blue"], "script-stated", "1", "writer")
    b.setValues(cup, "state.state", ["full"], "script-stated", "1", "writer", scene="1")
    b.setValues(coat, "piece.garment", ["raincoat"], "creator-approved", "decision", "creator")

    for item, scenes in ((kitchen, "13"), (street, "2"), (ana, "12"), (marco, "13"),
                         (cup, "13"), (letter, "2"), (umbrella, "2")):
        for s in scenes:
            b.link(item, s)
    b.link(coat, "2", ana.id)

    fm = frontmatter.empty()
    fm.title.title = "THE BLUE CUP"
    fm.title.subtitle = "A neutral test film"
    fm.title.author = "Test Author"
    fm.pitch.include = frontmatter.ON
    fm.pitch.logline = "Two people wait out the rain in a small kitchen."
    frontmatter.save(f, fm)

    notes = annotations.Annotations(f)
    notes.add("note", "1", text="The rain is heard through the whole scene.")
    notes.add("shot", "1", text="Wide on the table, both of them in frame.")

    sync.accept(f, sync.run(f, b, load(SCRIPT), "2026-10-31T12:00:00Z"))

    f.writeText(f.part("script").path, EDITED)
    b.link(ana, "2.A")
    b.link(letter, "2.A")
    sync.accept(f, sync.run(f, b, load(EDITED), "2026-10-31T13:00:00Z"))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
