# a film's front matter (front-matter/record/1), no wx: the title page and
# the overview, pitch and argument pages, kept as the film's
# `settings/front-matter.json` (part `front-matter`, a mocap-contracts
# FrontMatter). a film without the file has an empty one: nothing filled
# in, every optional page left out.

import mocap_contracts as mc

PART = "front-matter"
PATH = "settings/front-matter.json"

ON = mc.Flag.Value("FLAG_ON")
OFF = mc.Flag.Value("FLAG_OFF")


# an empty front matter: no text, the pages left out, the overview listing
# cast, sets and acts once included
def empty():
    fm = mc.FrontMatter()
    fm.title.SetInParent()
    fm.overview.include = OFF
    fm.overview.cast = ON
    fm.overview.sets = ON
    fm.overview.acts = ON
    fm.pitch.include = OFF
    fm.argument.include = OFF

    return fm


# the film's front matter; an invalid file is a film problem and an empty
# one is returned
def load(film):
    p = film.part(PART)

    if p is None or not (film.root / p.path).exists():
        return empty()

    try:
        return mc.from_json(mc.FrontMatter, film.readText(p.path))
    except mc.ContractError as e:
        film.problem(_("Front matter"), p.path, str(e))

        return empty()


# write fm; a film made before the part existed gets it first. nothing is
# written when fm is what the file holds
def save(film, fm, by="creator"):
    if film.part(PART) is None:
        film.addPart(PART, PATH)

    rel = film.part(PART).path
    text = mc.to_json(fm)

    if (film.root / rel).exists() and film.readText(rel) == text:
        return False

    film.writeText(rel, text, by)

    return True


def isOn(flag):
    return flag == ON
