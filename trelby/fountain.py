# Fountain (spec 1.1) as the writer's native format, without wx.
#
# parse() splits a .fountain text into the editor's elements and keeps, for
# each one, its exact source (raw) and the source before it that the editor
# does not show (pre: blank lines, boneyard, synopses, sections below level
# 1, page breaks). generate() lines the editor's current elements up with
# the ones parsed when the file was opened: an element that did not change
# is written back from its raw source, an edited or new one is written in
# canonical Fountain, and the hidden source travels with the element it
# preceded. So open -> save -> open is byte-identical, and an edit only
# rewrites what it touched.
#
# Mapping (element type <-> Fountain):
#   scene       INT./EXT./EST./I/E heading, or forced ".X"; a trailing
#               scene number "#12#" is the line's num, not in the text
#   action      any other paragraph; forced "!X" when it would read as
#               something else
#   character   upper-case cue followed by dialogue, or forced "@X"; the
#               dual-dialogue mark "^" is kept in the source
#   paren       "(...)" line inside a dialogue block
#   dialogue    the other lines of a dialogue block; an empty line is "  "
#   transition  upper-case "...TO:" alone, or forced "> X"
#   shot        upper-case line alone, ending in two spaces (Trelby's own
#               convention; other Fountain tools read it as action)
#   note        a paragraph that is one [[note]]
#   act break   level-1 section "# X"
#   title page  key: value lines at the top; Titles is rebuilt from them

import difflib
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import trelby.pml as pml
import trelby.screenplay as screenplay
import trelby.scenenumbers as scenenumbers
import trelby.titles as titles
import trelby.util as util
from trelby.line import Line

SCENE_RE = re.compile(r"^(INT\.?/EXT|INT/EXT|EXT/INT|I/E|INT|EXT|EST)[. ]", re.I)

# trailing scene number, "#12#", "#1A#", "#I-1-A#"
SCENE_NUMBER_RE = re.compile(r"\s*#[A-Za-z0-9.\-]+#\s*$")

# trailing dual-dialogue mark on a character cue
DUAL_RE = re.compile(r"\s*\^\s*$")

# first line of a title page: "Key: value" or "Key:"
TITLE_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 _\-]*):(?:\s+(.*?))?\s*$")

# title page value on its own line
TITLE_CONT_RE = re.compile(r"^(?:\t| {3,})(.*?)\s*$")


@dataclass
class Element:
    lt: int
    # as the editor holds it: lines joined by "\n"
    text: str
    # exact source of the element, line endings included
    raw: str = ""
    # exact source between the previous element and this one
    pre: str = ""
    # scene number or dual-dialogue mark, kept when the element is edited
    decor: str = ""


@dataclass
class Source:
    bom: str = ""
    eol: str = "\n"
    # raw title page block (without the blank line after it)
    title: str = ""
    # Titles built from it, as saved (titlesKey), to tell if it was edited
    titlesKey: str = ""
    elements: List[Element] = field(default_factory=list)
    # source after the last element
    tail: str = ""


# whether fileName is opened and saved as Fountain
def isFountain(fileName: str) -> bool:
    return fileName.lower().endswith(".fountain")


def _content(ln: str) -> str:
    return ln.rstrip("\r\n")


def _isBlank(s: str) -> bool:
    return s.strip() == ""


# lines that are not elements: synopsis, section below level 1, page break
def _isHidden(s: str) -> bool:
    s = s.lstrip()

    return s.startswith("=") or s.startswith("##")


def _isTitleKey(s: str) -> bool:
    if not TITLE_KEY_RE.match(s):
        return False

    # "FADE IN:" is a transition, not a key
    return not (s.isupper() and s.rstrip().endswith(":"))


def _hasLetter(s: str) -> bool:
    return any(c.isalpha() for c in s)


def _isUpper(s: str) -> bool:
    return _hasLetter(s) and s == s.upper()


def _isScene(s: str) -> bool:
    if s.startswith("."):
        return len(s) > 1 and s[1].isalnum()

    return bool(SCENE_RE.match(s))


def _isTransition(s: str) -> bool:
    if s.startswith(">"):
        return not s.endswith("<")

    return _isUpper(s) and s.endswith("TO:")


def _isCue(s: str) -> bool:
    if s.startswith("@"):
        return len(s) > 1

    name = DUAL_RE.sub("", s).split("(")[0].rstrip()

    return _isUpper(name)


def _isParen(s: str) -> bool:
    return s.startswith("(") and s.endswith(")")


def _isNote(s: str) -> bool:
    return s.startswith("[[") and s.endswith("]]") and s.find("]]") == len(s) - 2


# the scene number in a scene heading's decor ("  #12.A#" -> "12.A"), ""
# if none
def sceneNum(decor: str) -> str:
    d = decor.strip()

    if d.startswith("#") and d.endswith("#") and len(d) > 2:
        return d[1:-1]

    return ""


def _splitSuffix(s: str, rx: re.Pattern) -> Tuple[str, str]:
    m = rx.search(s)

    if not m:
        return (s, "")

    return (s[: m.start()], s[m.start() :])


# classify one paragraph (lines without line endings) into elements:
# [(lt, text, decor, number of lines)]
def classify(lines: List[str]) -> List[Tuple[int, str, str, int]]:
    first = lines[0]
    s = first.strip()

    def rest(n):
        if n < len(lines):
            return classify(lines[n:])

        return []

    if s.startswith("!"):
        i = first.index("!")
        body = [first[:i] + first[i + 1 :]] + lines[1:]

        return [(screenplay.ACTION, "\n".join(body), "", len(lines))]

    if s.startswith("#"):
        return [(screenplay.ACTBREAK, s[1:].strip(), "", 1)] + rest(1)

    if _isScene(s):
        if s.startswith("."):
            s = s[1:]

        text, decor = _splitSuffix(s, SCENE_NUMBER_RE)

        return [(screenplay.SCENE, text, decor, 1)] + rest(1)

    whole = "\n".join(lines).strip()

    if _isNote(whole):
        return [(screenplay.NOTE, whole[2:-2], "", len(lines))]

    if len(lines) == 1 and _isTransition(s):
        if s.startswith(">"):
            s = s[1:].strip()

        return [(screenplay.TRANSITION, s, "", 1)]

    if _isCue(s) and (len(lines) > 1 or s.startswith("@")):
        if s.startswith("@"):
            s = s[1:]

        name, decor = _splitSuffix(s, DUAL_RE)
        ret = [(screenplay.CHARACTER, name, decor, 1)]

        i = 1
        while i < len(lines):
            ln = lines[i].strip()

            if _isParen(ln):
                ret.append((screenplay.PAREN, ln, "", 1))
                i += 1

                continue

            dlg = []
            while i < len(lines) and not _isParen(lines[i].strip()):
                dlg.append(lines[i].strip())
                i += 1

            ret.append((screenplay.DIALOGUE, "\n".join(dlg), "", len(dlg)))

        return ret

    if len(lines) == 1 and first.endswith("  ") and _isUpper(s):
        return [(screenplay.SHOT, s, "", 1)]

    return [(screenplay.ACTION, "\n".join(lines), "", len(lines))]


def parse(text: str) -> Source:
    src = Source()

    if text.startswith("\ufeff"):
        src.bom = "\ufeff"
        text = text[1:]

    m = re.search(r"\r?\n", text)
    if m:
        src.eol = m.group(0)

    lines = text.splitlines(keepends=True)
    n = len(lines)
    i = 0

    if lines and _isTitleKey(_content(lines[0])):
        while i < n and not _isBlank(_content(lines[i])):
            i += 1

        src.title = "".join(lines[:i])

    pending = ""

    while i < n:
        c = _content(lines[i])

        if _isBlank(c) or _isHidden(c):
            pending += lines[i]
            i += 1

            continue

        if c.lstrip().startswith("/*"):
            j = i
            tail = c.lstrip()[2:]

            while "*/" not in tail and j + 1 < n:
                j += 1
                tail = _content(lines[j])

            pending += "".join(lines[i : j + 1])
            i = j + 1

            continue

        # a paragraph: up to a blank or hidden line. inside a dialogue
        # block, a line of two spaces is an empty dialogue line.
        cs = c.strip()
        dialogue = _isCue(cs) and not (cs.startswith("!") or _isScene(cs))
        j = i + 1

        while j < n:
            cj = _content(lines[j])

            if _isBlank(cj):
                # a run of "  " lines followed by more dialogue
                m = j
                while dialogue and m < n and _isBlank(_content(lines[m])):
                    if len(_content(lines[m])) < 2:
                        break
                    m += 1

                if not (dialogue and m > j and m < n and not _isBlank(_content(lines[m]))):
                    break

            elif _isHidden(cj) or cj.lstrip().startswith("/*"):
                break

            j += 1

        k = i
        for lt, etext, decor, cnt in classify([_content(ln) for ln in lines[i:j]]):
            src.elements.append(
                Element(
                    lt,
                    util.toInputStr(etext),
                    "".join(lines[k : k + cnt]),
                    pending,
                    decor,
                )
            )
            pending = ""
            k += cnt

        i = j

    src.tail = pending

    return src


# title page values without Fountain emphasis markup
def _titleValue(s: str) -> str:
    return util.toInputStr(s.strip().strip("_*").strip())


# title page block -> [(key, [values])]
def parseTitle(block: str) -> List[Tuple[str, List[str]]]:
    ret = []

    for ln in block.splitlines():
        m = TITLE_KEY_RE.match(ln)
        cont = TITLE_CONT_RE.match(ln)

        if cont and ret:
            ret[-1][1].append(_titleValue(cont.group(1)))
        elif m:
            ret.append((m.group(1), [_titleValue(m.group(2))] if m.group(2) else []))

    return ret


# Titles for a parsed title page, laid out like Trelby's defaults
def makeTitles(block: str) -> titles.Titles:
    ret = titles.Titles()

    if not block:
        return ret

    page = []
    leftY = 220.0
    centerY = 150.0

    for key, values in parseTitle(block):
        values = [v for v in values if v]
        k = key.lower()

        if not values:
            continue

        if k == "title":
            page.append(
                titles.TitleString(
                    values, y=105.0, size=24, isBold=True, font=pml.HELVETICA
                )
            )
        elif k in ("author", "authors"):
            page.append(titles.TitleString(["by", ""] + values, y=120.46))
        elif k == "contact":
            page.append(titles.TitleString(values, 15.0, 248.46, False))
        else:
            items = [key + ": " + values[0]] if len(values) == 1 else [key + ":"] + values

            if k in ("credit", "source"):
                page.append(titles.TitleString(items, y=centerY))
                centerY += 5
            else:
                page.append(titles.TitleString(items, 15.0, leftY, False))
                leftY -= 5

    if page:
        ret.pages.append(page)

    return ret


def titlesKey(t: titles.Titles) -> str:
    return "\n#Title-Page\n".join("\n".join(str(ts) for ts in pg) for pg in t.pages)


# Fountain title page lines for the given Titles
def generateTitle(t: titles.Titles) -> List[str]:
    ret = []
    keyRe = re.compile(r"^([A-Za-z][A-Za-z0-9 _\-]*):\s*(.*)$")
    titleDone = False

    for pg in t.pages:
        for ts in pg:
            items = list(ts.items)

            if not any(items):
                continue

            m = keyRe.match(items[0])

            if not titleDone and ts.isBold and ts.isCentered:
                key = "Title"
                titleDone = True
            elif items[0] == "by":
                key = "Author"
                items = items[1:]
            elif m:
                key = m.group(1)
                items = ([m.group(2)] if m.group(2) else []) + items[1:]
            else:
                key = "Contact"

            items = [it for it in items if it]

            if len(items) == 1:
                ret.append("%s: %s" % (key, items[0]))
            elif items:
                ret.append(key + ":")
                ret.extend("    " + it for it in items)

    return ret


# the editor's elements: [(lt, text, num)], text lines joined by "\n",
# num the scene number of a scene heading ("" for other types)
def elementsOf(sp) -> List[Tuple[int, str, str]]:
    ret = []
    cur = ""
    num = None

    for ln in sp.lines:
        if num is None:
            num = ln.num

        cur += ln.text

        if ln.lb == screenplay.LB_LAST:
            ret.append((ln.lt, cur, num if ln.lt == screenplay.SCENE else ""))
            cur = ""
            num = None
        elif ln.lb == screenplay.LB_SPACE:
            cur += " "
        elif ln.lb == screenplay.LB_FORCED:
            cur += "\n"

    return ret


# Fountain source -> Lines (unwrapped; reformatAll wraps them)
def toLines(src: Source) -> List[Line]:
    ret = []

    for e in src.elements:
        parts = e.text.split("\n")

        for i, part in enumerate(parts):
            lb = screenplay.LB_LAST if i == len(parts) - 1 else screenplay.LB_FORCED
            num = sceneNum(e.decor) if (i == 0 and e.lt == screenplay.SCENE) else ""
            ret.append(Line(lb, e.lt, part, num))

    if not ret:
        ret.append(Line(screenplay.LB_LAST, screenplay.SCENE))

    return ret


# build a Screenplay from a .fountain file's text
def load(text: str, cfgGl):
    src = parse(text)

    sp = screenplay.Screenplay(cfgGl)
    sp.lines = toLines(src)
    sp.titles = makeTitles(src.title)
    sp.headers.addDefaults()

    src.titlesKey = titlesKey(sp.titles)
    sp.fountainSource = src
    sp.sceneNumbersIssued = {ln.num for ln in sp.lines if ln.num}
    sp.sceneTextsIssued = scenenumbers.sceneTexts(sp)

    sp.reformatAll()
    sp.paginate()
    sp.locations.refresh(sp.getSceneNames())

    return sp


# candidate Fountain spellings of one element, natural first
def _candidates(lt: int, text: str, decor: str) -> List[str]:
    if lt == screenplay.SCENE:
        return [text + decor, "." + text + decor]
    elif lt == screenplay.ACTION:
        return [text, "!" + text]
    elif lt == screenplay.CHARACTER:
        return [text + decor, "@" + text + decor]
    elif lt == screenplay.TRANSITION:
        return [text, "> " + text]
    elif lt == screenplay.SHOT:
        return [text + "  "]
    elif lt == screenplay.NOTE:
        return ["[[" + text + "]]"]
    elif lt == screenplay.ACTBREAK:
        return ["# " + text]
    elif lt == screenplay.DIALOGUE:
        return ["\n".join(ln if ln else "  " for ln in text.split("\n"))]
    else:
        return [text]


# Fountain lines for one element. inDialogue: it follows a character, paren
# or dialogue; cued: a character followed by dialogue; atStart: first thing
# in the file. Returns (lines, ok), ok False if it will not read back as it
# is.
def _render(lt, text, decor, inDialogue, cued, atStart):
    cands = _candidates(lt, text, decor)

    for cand in cands:
        lines = cand.split("\n")

        if atStart and _isTitleKey(lines[0]):
            continue

        if lt in (screenplay.DIALOGUE, screenplay.PAREN):
            got = classify(["@X"] + lines)[1:]
        elif lt == screenplay.CHARACTER and cued:
            got = classify(lines + ["x"])[:1]
        else:
            got = classify(lines)

        if [g[:3] for g in got] == [(lt, text, decor)]:
            ok = inDialogue or lt not in (screenplay.DIALOGUE, screenplay.PAREN)

            return (lines, ok)

    return (cands[0].split("\n"), False)


# what generate() could not write so that it reads back the same
@dataclass
class Result:
    text: str
    source: Source
    # [(lt, text)] of elements that will read back differently
    lost: List[Tuple[int, str]] = field(default_factory=list)


def generate(sp) -> Result:
    src: Optional[Source] = sp.fountainSource
    old = src or Source()
    eol = old.eol
    dialogueTypes = (screenplay.CHARACTER, screenplay.DIALOGUE, screenplay.PAREN)
    spokenTypes = (screenplay.DIALOGUE, screenplay.PAREN)

    def key(lt, text, num):
        if sp.cfg.getType(lt).export.isCaps:
            text = util.upper(text)

        return (lt, text, num)

    def oldKey(e):
        return key(e.lt, e.text, sceneNum(e.decor) if e.lt == screenplay.SCENE else "")

    cur = [key(*el) for el in elementsOf(sp) if el[1].strip()]
    oldKeys = [oldKey(e) for e in old.elements]

    curTitles = titlesKey(sp.titles)
    if src and curTitles == old.titlesKey:
        title = old.title
    else:
        title = "".join(ln + eol for ln in generateTitle(sp.titles))

    out = []
    lost = []

    # prevLt: type of the last element written; prevOld: its index in
    # old.elements, None for a new one; carry: hidden source of deleted
    # elements, written before the next element
    st = {"prevLt": None, "prevOld": None, "carry": "", "any": False}

    def put(s):
        if not s:
            return

        # the previous element was the last line of a file without a final
        # newline
        if out and s and not out[-1].endswith("\n"):
            out.append(eol)

        out.append(s)

    # separator before an element that is not glued to its predecessor
    def sep(lt):
        if lt in spokenTypes and st["prevLt"] in dialogueTypes:
            return ""

        return eol if (st["any"] or title) else ""

    def emitOld(idx):
        e = old.elements[idx]
        pre = e.pre

        # glued to an element that is no longer before it
        if "\n" not in pre and st["prevOld"] != idx - 1:
            pre = sep(e.lt)

        put(st["carry"] + pre + e.raw)
        st.update(prevLt=e.lt, prevOld=idx, carry="", any=True)

    def emitNew(ci, pre, decor):
        lt, text, num = cur[ci]

        # a scene number not written as it was: in canonical form
        if lt == screenplay.SCENE and sceneNum(decor) != num:
            decor = " #%s#" % num if num else ""
        inDialogue = st["prevLt"] in dialogueTypes
        cued = (
            lt == screenplay.CHARACTER
            and ci + 1 < len(cur)
            and cur[ci + 1][0] in spokenTypes
        )
        atStart = not (st["any"] or title)
        lines, ok = _render(lt, text, decor, inDialogue, cued, atStart)

        if not ok:
            lost.append((lt, text))

        if pre is None or "\n" not in pre:
            pre = sep(lt)

        put(st["carry"] + pre + "".join(ln + eol for ln in lines))
        st.update(prevLt=lt, prevOld=None, carry="", any=True)

    def drop(idx):
        pre = old.elements[idx].pre

        if not _isBlank(pre):
            st["carry"] += pre

    sm = difflib.SequenceMatcher(None, oldKeys, cur, autojunk=False)

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                emitOld(i1 + k)

            continue

        # edited in place: keep the hidden source before it and, same type,
        # its dual mark, and its scene number's spacing while the number is
        # the same
        pairs = min(i2 - i1, j2 - j1)

        for k in range(j2 - j1):
            if k < pairs:
                e = old.elements[i1 + k]
                decor = e.decor if e.lt == cur[j1 + k][0] else ""
                emitNew(j1 + k, e.pre, decor)
            else:
                emitNew(j1 + k, None, "")

        for k in range(pairs, i2 - i1):
            drop(i1 + k)

    put(st["carry"])

    if src:
        put(old.tail)

    body = "".join(out)

    # the title page needs a blank line after it
    if title and body and not body.startswith(("\n", "\r\n")):
        body = eol + body

    text = old.bom + title + body
    newSrc = parse(text)
    newSrc.titlesKey = curTitles

    got = [oldKey(e) for e in newSrc.elements]
    if got != cur:
        sm = difflib.SequenceMatcher(None, cur, got, autojunk=False)

        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                for k in range(i1, i2):
                    if cur[k][:2] not in lost:
                        lost.append(cur[k][:2])

    return Result(text, newSrc, lost)
