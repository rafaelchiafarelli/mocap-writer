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


# the printed title page of fm: the places fountain.makeTitles uses for
# the title, the authors and the contact, with the subtitle and the
# episode centered under the title
def titlePages(fm):
    import trelby.pml as pml
    import trelby.titles as titles

    t = fm.title
    ret = titles.Titles()

    if titleEmpty(fm):
        return ret

    page = []

    if t.title:
        page.append(titles.TitleString([t.title], y=105.0, size=24, isBold=True,
                                       font=pml.HELVETICA))

    y = 116.0

    for text in (t.subtitle, _("Episode %s") % t.episode if t.episode else ""):
        if text:
            page.append(titles.TitleString([text], y=y, size=14))
            y += 7.0

    authors = [a for a in [t.author, *t.co_authors] if a]

    if authors:
        page.append(titles.TitleString(["by", ""] + authors, y=y + 8.0))

    if t.email:
        page.append(titles.TitleString([t.email], 15.0, 248.46, False))

    ret.pages.append(page)

    return ret


# the script sp shows fm's title page: its Fountain title block and its
# title pages, so the next save writes exactly that block
def applyTitle(sp, fm):
    import trelby.fountain as fountain

    if sp.fountainSource is None:
        sp.fountainSource = fountain.Source()

    src = sp.fountainSource
    src.title = titleBlock(fm, src.eol)
    sp.titles = titlePages(fm)
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


# print/1: the included pages, printed after the title page

# the overview's text lines: [(text, bold)]
def overviewLines(fm, b, sp):
    import trelby.acts as acts
    import trelby.biblelinks as biblelinks

    out = [(_("OVERVIEW"), True), ("", False)]

    def tree(map_):
        lines = []

        def walk(parentId, depth):
            for it in b.children(map_, parentId):
                lines.append(("    " * depth + it.name, False))
                walk(it.id, depth + 1)

        if b is not None:
            walk(None, 0)

        return lines or [("-", False)]

    if isOn(fm.overview.cast):
        out += [(_("Cast"), True)] + tree("character") + [("", False)]

    if isOn(fm.overview.sets):
        out += [(_("Sets"), True)] + tree("set") + [("", False)]

    if isOn(fm.overview.acts):
        out.append((_("Act breakdown"), True))
        sp.paginate()
        scenes = biblelinks.scenesWithLines(sp)
        parts = acts.actsOf(sp)

        if not parts:
            out.append((_("No act breaks in the script."), False))

        for i, act in enumerate(parts):
            end = parts[i + 1].line if i + 1 < len(parts) else len(sp.lines)
            inAct = [(n, f, l) for n, f, l in scenes if act.line <= f < end]
            pages = (sp.line2page(act.line), sp.line2page(end - 1))
            nums = ", ".join(n for n, _f, _l in inAct) or "-"
            out.append((_("%s: pages %d-%d, %d scenes (%s)") % (
                act.name or _("Opening"), pages[0], pages[1], act.scenes, nums), False))

    return out


# add the included pages to the PML document doc; returns how many pages
# were added (they are not counted as the script's pages)
def addPages(doc, fm, b, sp):
    import trelby.pml as pml

    sections = []

    if isOn(fm.overview.include):
        sections.append(overviewLines(fm, b, sp))

    if isOn(fm.pitch.include):
        p = fm.pitch
        sections.append([
            (_("PITCH"), True), ("", False), (p.pitch, False), ("", False),
            (_("Logline"), True), (p.logline, False), ("", False),
            (_("Target audience"), True), (p.target_audience, False),
        ])

    if isOn(fm.argument.include):
        lines = [(_("ARGUMENT"), True), ("", False)]

        for para in fm.argument.text.split("\n"):
            lines.append((para, False))

        sections.append(lines)

    if not sections:
        return 0

    tf = pml.TextFormatter(doc.w, doc.h, 25.4, 12)
    first = True

    for lines in sections:
        if not first:
            tf.createPage()

        first = False

        for text, bold in lines:
            if not text:
                tf.addSpace(5)
            elif bold:
                tf.addText(text, style=pml.BOLD)
            else:
                tf.addWrappedText(text, "")

    for pg in tf.doc.pages:
        doc.add(pg)

    return len(tf.doc.pages)
