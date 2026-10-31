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


# title/1: the script's Fountain title block is written from the record

def titleEmpty(fm):
    t = fm.title

    return not any((t.title, t.subtitle, t.episode, t.author, t.email, *t.co_authors))


# the title block for fm's title page ("" when it is empty): the standard
# keys Title, Credit, Author(s), Contact, and Subtitle / Episode, which
# other tools show as they are
def titleBlock(fm, eol="\n"):
    t = fm.title

    if titleEmpty(fm):
        return ""

    lines = []

    def put(key, values):
        values = [v for v in values if v]

        if len(values) == 1:
            lines.append("%s: %s" % (key, values[0]))
        elif values:
            lines.append(key + ":")
            lines.extend("    " + v for v in values)

    put("Title", [t.title])
    put("Subtitle", [t.subtitle])
    put("Episode", [t.episode])
    authors = [a for a in [t.author, *t.co_authors] if a]

    if authors:
        lines.append("Credit: Written by")
        put("Authors" if len(authors) > 1 else "Author", authors)

    put("Contact", [t.email])

    return "".join(ln + eol for ln in lines)


# a title page from a Fountain title block: Title (a second line is the
# subtitle when there is no Subtitle key), Subtitle, Episode, Author(s)
# (the first is the author, the others co-authors), the e-mail among the
# Contact lines (the first with an @)
def fromBlock(block):
    import trelby.fountain as fountain

    fm = empty()
    t = fm.title

    for key, values in fountain.parseTitle(block):
        k = key.lower()
        values = [v for v in values if v]

        if not values:
            continue

        if k == "title":
            t.title = values[0]

            if len(values) > 1 and not t.subtitle:
                t.subtitle = values[1]
        elif k == "subtitle":
            t.subtitle = values[0]
        elif k in ("episode", "episode number"):
            t.episode = values[0]
        elif k in ("author", "authors", "written by"):
            names = [n.strip() for v in values for n in v.split(" & ")]
            t.author = names[0]
            t.co_authors.extend(names[1:])
        elif k == "contact":
            mail = next((v for v in values if "@" in v), None)

            if mail:
                t.email = mail

    return fm.title


# the script sp shows fm's title page: its Fountain title block and the
# title pages built from it, so the next save writes exactly that block
def applyTitle(sp, fm):
    import trelby.fountain as fountain

    if sp.fountainSource is None:
        sp.fountainSource = fountain.Source()

    src = sp.fountainSource
    src.title = titleBlock(fm, src.eol)
    sp.titles = fountain.makeTitles(src.title)
    src.titlesKey = fountain.titlesKey(sp.titles)


# a film's script and its front matter agree: a record with an empty title
# page takes the script's title block once (no title is lost), then the
# script shows the record's. returns the front matter
def syncTitle(film, sp):
    fm = load(film)
    block = sp.fountainSource.title if sp.fountainSource else ""

    if titleEmpty(fm) and block:
        fm.title.CopyFrom(fromBlock(block))
        save(film, fm, "writer")

    applyTitle(sp, fm)

    return fm
