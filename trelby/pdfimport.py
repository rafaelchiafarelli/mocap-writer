# PDF import: a master-scene screenplay PDF with selectable text becomes a
# list of Lines, each line classified by its left indent (or right edge, or
# center) as declared in a layout profile. Deterministic, no guessing: a line
# that matches no rule of the profile stops the import with its page and line.
#
# Command line (writes one .fountain per PDF):
#   python -m trelby.pdfimport import <pdf>... --profile <file> --out <dir>
#   python -m trelby.pdfimport probe <pdf>
#
# The profile format is described in trelby/pdfprofiles/CLAUDE.md.

import argparse
import os
import re
import sys
import tomllib
from dataclasses import dataclass, field
from typing import List, Optional

import trelby.screenplay as screenplay
from trelby.line import Line

ELEMENTS = {
    "scene": screenplay.SCENE,
    "action": screenplay.ACTION,
    "character": screenplay.CHARACTER,
    "parenthetical": screenplay.PAREN,
    "dialogue": screenplay.DIALOGUE,
    "transition": screenplay.TRANSITION,
}

# pseudo-element: scene heading if the line starts with one of the profile's
# scene_prefixes, action otherwise (master-scene scripts share that indent)
SCENE_ACTION = "scene_action"

# names used in traces and messages
TYPE_NAMES = {v: k for k, v in ELEMENTS.items()}


class PdfImportError(Exception):
    def __init__(self, msg, page=None, lineNo=None):
        Exception.__init__(self, msg)
        self.page = page
        self.lineNo = lineNo


@dataclass
class Rule:
    element: str
    # exactly one of x (left edge), x1 (right edge), xc (center) is set
    edge: str
    pos: float
    tolerance: float

    def matches(self, seg):
        return abs(seg.edgePos(self.edge) - self.pos) <= self.tolerance

    def describe(self):
        return "%s=%g" % (self.edge, self.pos)


@dataclass
class Furniture:
    pattern: re.Pattern
    topMin: Optional[float]
    topMax: Optional[float]

    def matches(self, text, top):
        if self.topMin is not None and top < self.topMin:
            return False
        if self.topMax is not None and top > self.topMax:
            return False
        return bool(self.pattern.search(text))


@dataclass
class Profile:
    name: str
    tolerance: float
    segmentGap: float
    paragraphGap: float
    skipPages: int
    scenePrefixes: List[str]
    rules: List[Rule]
    dualLeft: List[Rule]
    dualRight: List[Rule]
    furniture: List[Furniture]
    characterSuffixes: List[re.Pattern]
    sceneNumberPattern: Optional[re.Pattern]
    sceneNumberLeft: Optional[Rule]
    sceneNumberRight: Optional[Rule]


def _rules(items, tolerance, where):
    ret = []
    for i, it in enumerate(items):
        _checkKeys(it, RULE_KEYS, "%s[%d]" % (where, i))
        el = it.get("element")
        if el not in ELEMENTS and el != SCENE_ACTION:
            raise PdfImportError(
                "profile: %s[%d]: unknown element %r" % (where, i, el)
            )
        edges = [e for e in ("x", "x1", "xc") if e in it]
        if len(edges) != 1:
            raise PdfImportError(
                "profile: %s[%d]: needs exactly one of x, x1, xc" % (where, i)
            )
        ret.append(
            Rule(el, edges[0], float(it[edges[0]]), float(it.get("tolerance", tolerance)))
        )
    return ret


def loadProfile(path):
    with open(path, "rb") as f:
        try:
            d = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise PdfImportError("profile %s: %s" % (path, e))

    return parseProfile(d, os.path.splitext(os.path.basename(path))[0])


# the keys a profile may hold; anything else is an error, because in TOML a
# key written after a [table] header silently belongs to that table
PROFILE_KEYS = {
    "name", "description", "tolerance", "segment_gap", "paragraph_gap",
    "skip_pages", "scene_prefixes", "character_suffix", "indent", "drop",
    "dual", "scene_numbers",
}
RULE_KEYS = {"element", "x", "x1", "xc", "tolerance"}
DROP_KEYS = {"pattern", "top_min", "top_max"}
DUAL_KEYS = {"left", "right"}
SCENE_NUMBER_KEYS = {"left", "right", "tolerance", "pattern"}


def _checkKeys(d, allowed, where):
    extra = sorted(set(d) - allowed)
    if extra:
        raise PdfImportError("profile: %s: unknown key(s) %s" % (where, ", ".join(extra)))


def parseProfile(d, defaultName="profile"):
    _checkKeys(d, PROFILE_KEYS, "top level")
    tol = float(d.get("tolerance", 3.0))
    if not d.get("indent"):
        raise PdfImportError("profile: no [[indent]] rules")

    dual = d.get("dual", {})
    _checkKeys(dual, DUAL_KEYS, "dual")
    sn = d.get("scene_numbers", {})
    _checkKeys(sn, SCENE_NUMBER_KEYS, "scene_numbers")
    for i, f in enumerate(d.get("drop", [])):
        _checkKeys(f, DROP_KEYS, "drop[%d]" % i)
        if "pattern" not in f:
            raise PdfImportError("profile: drop[%d]: no pattern" % i)
    snRule = lambda k: Rule("scene", "x", float(sn[k]), float(sn.get("tolerance", tol))) if k in sn else None

    return Profile(
        name=d.get("name", defaultName),
        tolerance=tol,
        segmentGap=float(d.get("segment_gap", 28.0)),
        paragraphGap=float(d.get("paragraph_gap", 18.0)),
        skipPages=int(d.get("skip_pages", 0)),
        scenePrefixes=[p.upper() for p in d.get("scene_prefixes", [])],
        rules=_rules(d["indent"], tol, "indent"),
        dualLeft=_rules(dual.get("left", []), tol, "dual.left"),
        dualRight=_rules(dual.get("right", []), tol, "dual.right"),
        furniture=[
            Furniture(re.compile(f["pattern"]), f.get("top_min"), f.get("top_max"))
            for f in d.get("drop", [])
        ],
        characterSuffixes=[re.compile(p) for p in d.get("character_suffix", [])],
        sceneNumberPattern=re.compile(sn.get("pattern", r"^\d+[A-Z]*\.?$")) if sn else None,
        sceneNumberLeft=snRule("left"),
        sceneNumberRight=snRule("right"),
    )


@dataclass
class Word:
    text: str
    x0: float
    x1: float
    top: float


@dataclass
class Segment:
    words: List[Word]

    @property
    def x0(self):
        return self.words[0].x0

    @property
    def x1(self):
        return self.words[-1].x1

    @property
    def text(self):
        return " ".join(w.text for w in self.words)

    def edgePos(self, edge):
        if edge == "x":
            return self.x0
        if edge == "x1":
            return self.x1
        return (self.x0 + self.x1) / 2.0


@dataclass
class PdfLine:
    page: int  # 1-based
    lineNo: int  # 1-based, within the page, counting every text line
    top: float
    words: List[Word]
    segments: List[Segment] = field(default_factory=list)
    sceneNumber: Optional[str] = None

    @property
    def text(self):
        return " ".join(w.text for w in self.words)


# the text lines of a PDF, as lists of words grouped by their top position.
# Each item: (page number, page height, [PdfLine]).
def extractPages(path):
    import pdfplumber

    pages = []
    try:
        pdf = pdfplumber.open(path)
    except Exception as e:
        raise PdfImportError("cannot open %s: %s" % (path, e))

    with pdf:
        for p in pdf.pages:
            words = p.extract_words(keep_blank_chars=False, use_text_flow=False)
            words = [Word(w["text"], w["x0"], w["x1"], w["top"]) for w in words]
            words.sort(key=lambda w: (w.top, w.x0))

            lines = []
            for w in words:
                if lines and abs(lines[-1].words[0].top - w.top) <= 2.0:
                    lines[-1].words.append(w)
                else:
                    lines.append(PdfLine(p.page_number, len(lines) + 1, w.top, [w]))

            for ln in lines:
                ln.words.sort(key=lambda w: w.x0)

            pages.append((p.page_number, float(p.height), lines))

    return pages


def _split(words, gap):
    segs = [Segment([words[0]])]
    for w in words[1:]:
        if w.x0 - segs[-1].x1 > gap:
            segs.append(Segment([w]))
        else:
            segs[-1].words.append(w)
    return segs


class _Trace:
    def __init__(self, out):
        self.out = out

    def add(self, ln, seg, decision, rule=""):
        if self.out is None:
            return
        x0 = seg.x0 if seg else ln.words[0].x0
        x1 = seg.x1 if seg else ln.words[-1].x1
        text = seg.text if seg else ln.text
        self.out.append(
            {
                "page": ln.page,
                "line": ln.lineNo,
                "top": round(ln.top, 1),
                "x0": round(x0, 1),
                "x1": round(x1, 1),
                "decision": decision,
                "rule": rule,
                "text": text,
            }
        )


@dataclass
class _Item:
    # one classified piece of text, in reading order
    lt: int
    text: str
    page: int
    top: float
    # "left"/"right" inside a dual-dialogue block, None otherwise
    column: Optional[str] = None
    dualBlock: int = -1


def _classify(seg, rules, profile):
    for r in rules:
        if r.matches(seg):
            el = r.element
            if el == SCENE_ACTION:
                up = seg.text.upper()
                if any(up.startswith(p) for p in profile.scenePrefixes):
                    return screenplay.SCENE, r
                return screenplay.ACTION, r
            return ELEMENTS[el], r
    return None, None


# classify every line of the PDF; returns a list of _Item.
def _items(pages, profile, trace, skipPages):
    items = []
    dualBlocks = 0
    inDual = False
    prevTop = None

    for pageNo, height, lines in pages:
        if pageNo <= skipPages:
            for ln in lines:
                trace.add(ln, None, "skipped page")
            continue

        prevTop = None
        inDual = False

        for ln in lines:
            text = ln.text.strip()

            dropped = False
            for f in profile.furniture:
                if f.matches(text, ln.top):
                    trace.add(ln, None, "dropped", f.pattern.pattern)
                    dropped = True
                    break
            if dropped:
                continue

            words = list(ln.words)

            # margin scene numbers
            if profile.sceneNumberPattern is not None:
                for rule in (profile.sceneNumberLeft, profile.sceneNumberRight):
                    if rule is None:
                        continue
                    for w in list(words):
                        seg = Segment([w])
                        if rule.matches(seg) and profile.sceneNumberPattern.match(w.text):
                            words.remove(w)
                            if ln.sceneNumber is None:
                                ln.sceneNumber = w.text.rstrip(".")
                            trace.add(ln, seg, "scene number", rule.describe())
                if not words:
                    continue

            segs = _split(words, profile.segmentGap)
            gap = None if prevTop is None else ln.top - prevTop
            prevTop = ln.top

            if inDual and gap is not None and gap > profile.paragraphGap:
                inDual = False

            if len(segs) >= 2 or inDual:
                if len(segs) > 2:
                    raise PdfImportError(
                        "page %d, line %d: %d text columns: %r"
                        % (ln.page, ln.lineNo, len(segs), ln.text),
                        ln.page,
                        ln.lineNo,
                    )

                if len(segs) == 2 and not inDual:
                    # a dual-dialogue block starts with two character names
                    lt0, _r0 = _classify(segs[0], profile.dualLeft, profile)
                    lt1, _r1 = _classify(segs[1], profile.dualRight, profile)
                    if lt0 != screenplay.CHARACTER or lt1 != screenplay.CHARACTER:
                        raise PdfImportError(
                            "page %d, line %d: two text columns that are not a "
                            "dual-dialogue start (x0 %.1f and %.1f): %r"
                            % (ln.page, ln.lineNo, segs[0].x0, segs[1].x0, ln.text),
                            ln.page,
                            ln.lineNo,
                        )
                    inDual = True
                    dualBlocks += 1

                for seg in segs:
                    lt, r, col = None, None, None
                    for col, rules in (("left", profile.dualLeft), ("right", profile.dualRight)):
                        lt, r = _classify(seg, rules, profile)
                        if lt is not None:
                            break
                    if lt is None:
                        raise PdfImportError(
                            "page %d, line %d: x0 %.1f matches no dual-dialogue "
                            "column rule: %r" % (ln.page, ln.lineNo, seg.x0, seg.text),
                            ln.page,
                            ln.lineNo,
                        )
                    trace.add(ln, seg, "dual %s %s" % (col, TYPE_NAMES[lt]), r.describe())
                    items.append(_Item(lt, seg.text, ln.page, ln.top, col, dualBlocks))
                continue

            seg = segs[0]
            lt, r = _classify(seg, profile.rules, profile)
            if lt is None:
                trace.add(ln, seg, "UNKNOWN INDENT")
                raise PdfImportError(
                    "page %d, line %d: indent x0 %.1f (right edge %.1f) matches "
                    "no rule of profile %r: %r"
                    % (ln.page, ln.lineNo, seg.x0, seg.x1, profile.name, seg.text),
                    ln.page,
                    ln.lineNo,
                )

            text = seg.text
            if lt == screenplay.SCENE and ln.sceneNumber:
                text += " #%s#" % ln.sceneNumber

            trace.add(ln, seg, TYPE_NAMES[lt], r.describe())
            items.append(_Item(lt, text, ln.page, ln.top))

    return items


def _stripSuffixes(name, profile):
    changed = True
    while changed:
        changed = False
        for p in profile.characterSuffixes:
            n = p.sub("", name).rstrip()
            if n != name:
                name = n
                changed = True
    return name


# group items into elements: [lt, [texts]].
def _elements(items, profile):
    elems = []
    prev = None
    lastSpeaker = None
    # inside a dual-dialogue block, each column continues from its own
    # previous item, not from the other column's item on the same row
    prevByColumn = {}

    def startsNew(it, prev):
        if prev is None or it.lt != prev.lt:
            return True
        if it.column != prev.column or it.dualBlock != prev.dualBlock:
            return True
        if it.lt in (screenplay.CHARACTER, screenplay.TRANSITION):
            return True
        if it.lt == screenplay.PAREN and it.text.startswith("("):
            return True
        if it.page != prev.page:
            # a speech cut by a page break goes on; anything else starts over
            return it.lt != screenplay.DIALOGUE
        return it.top - prev.top > profile.paragraphGap

    i = 0
    while i < len(items):
        it = items[i]

        if it.lt == screenplay.CHARACTER:
            it.text = _stripSuffixes(it.text, profile)

            # NAME (CONT'D) at the top of a page, after that same NAME's
            # speech at the end of the previous one: the speech goes on
            if (
                prev is not None
                and it.column is None
                and it.page != prev.page
                and prev.lt in (screenplay.DIALOGUE, screenplay.PAREN)
                and lastSpeaker == it.text
            ):
                i += 1
                continue

            lastSpeaker = it.text

        if it.column is None:
            before = prev
        else:
            before = prevByColumn.get((it.dualBlock, it.column))

        if startsNew(it, before):
            elems.append([it.lt, [it.text], it])
            if it.column is not None:
                prevByColumn[(it.dualBlock, it.column, "elem")] = elems[-1]
        elif it.column is None:
            elems[-1][1].append(it.text)
        else:
            prevByColumn[(it.dualBlock, it.column, "elem")][1].append(it.text)

        if it.column is not None:
            prevByColumn[(it.dualBlock, it.column)] = it
        prev = it
        i += 1

    # dual dialogue: the second (right) speaker of each block gets "^"
    seen = set()
    for e in elems:
        it = e[2]
        if it.column == "right" and e[0] == screenplay.CHARACTER and it.dualBlock not in seen:
            seen.add(it.dualBlock)
            e[1][0] += " ^"

    # in each dual block, all left-column elements come before the right ones
    out = []
    i = 0
    while i < len(elems):
        if elems[i][2].column is None:
            out.append(elems[i])
            i += 1
            continue
        block = elems[i][2].dualBlock
        j = i
        while j < len(elems) and elems[j][2].dualBlock == block and elems[j][2].column is not None:
            j += 1
        group = elems[i:j]
        out.extend(e for e in group if e[2].column == "left")
        out.extend(e for e in group if e[2].column == "right")
        i = j

    return [(lt, texts) for lt, texts, _it in out]


# import a PDF; returns a list of Lines that meets the importer contract
# (trelby/myimport.as-built.md). trace, if a list, receives one dict per
# piece of text with the decision taken for it.
def importPdf(path, profile, trace=None, skipPages=None):
    if skipPages is None:
        skipPages = profile.skipPages

    pages = extractPages(path)
    items = _items(pages, profile, _Trace(trace), skipPages)

    ret = []
    for lt, texts in _elements(items, profile):
        for t in texts:
            ret.append(Line(screenplay.LB_SPACE, lt, t))
        ret[-1].lb = screenplay.LB_LAST

    if not ret:
        raise PdfImportError("%s: no text found (a scanned PDF?)" % path)

    return ret


# the indents found in a PDF, for writing a profile. Returns text.
def probe(path, skipPages=0, segmentGap=28.0):
    pages = extractPages(path)
    stats = {}

    for pageNo, height, lines in pages:
        if pageNo <= skipPages:
            continue
        for ln in lines:
            segs = _split(ln.words, segmentGap)
            for si, seg in enumerate(segs):
                key = (round(seg.x0, 1), len(segs) > 1 and si or 0)
                st = stats.setdefault(key, {"count": 0, "samples": [], "x1": []})
                st["count"] += 1
                st["x1"].append(seg.x1)
                if len(st["samples"]) < 3:
                    st["samples"].append("p%d l%d: %s" % (ln.page, ln.lineNo, seg.text[:50]))

    out = ["%s: %d pages" % (path, len(pages))]
    if pages:
        out.append("page height: %.1f pt (x and top in points from the top left)" % pages[0][1])
    out.append("%8s %6s %6s %10s  samples" % ("x0", "col", "count", "x1 range"))
    for (x0, col), st in sorted(stats.items()):
        out.append(
            "%8.1f %6s %6d %4.0f-%-5.0f  %s"
            % (
                x0,
                col or "",
                st["count"],
                min(st["x1"]),
                max(st["x1"]),
                " | ".join(st["samples"]),
            )
        )
    return "\n".join(out)


def writeTrace(trace, path):
    cols = ["page", "line", "top", "x0", "x1", "decision", "rule", "text"]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in trace:
            f.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\n")


# a Screenplay holding the given lines, reformatted and paginated, with no
# title pages (a PDF's title page is skipped, not imported).
def toScreenplay(lines):
    import trelby.config as config
    import trelby.misc as misc
    import trelby.util as util

    if getattr(misc, "progPath", None) is None:
        misc.init(False)
        util.init(False)

    sp = screenplay.Screenplay(config.ConfigGlobal())
    sp.titles.pages = []
    sp.lines = lines
    sp.reformatAll()
    sp.paginate()
    return sp


def main(argv=None):
    import trelby.translations as translations

    translations.trelby_translations_load()

    ap = argparse.ArgumentParser(prog="python -m trelby.pdfimport")
    sub = ap.add_subparsers(dest="cmd", required=True)

    imp = sub.add_parser("import", help="PDF -> .fountain")
    imp.add_argument("pdf", nargs="+")
    imp.add_argument("--profile", required=True)
    imp.add_argument("--out", required=True, help="output directory")
    imp.add_argument("--skip-pages", type=int, default=None,
                     help="leading pages to skip (default: the profile's skip_pages)")
    imp.add_argument("--trace", action="store_true",
                     help="also write <name>.trace.tsv: every piece of text and its decision")

    pr = sub.add_parser("probe", help="list the indents found in a PDF")
    pr.add_argument("pdf")
    pr.add_argument("--skip-pages", type=int, default=0)
    pr.add_argument("--segment-gap", type=float, default=28.0)

    args = ap.parse_args(argv)

    if args.cmd == "probe":
        try:
            print(probe(args.pdf, args.skip_pages, args.segment_gap))
        except PdfImportError as e:
            print("error: %s" % e, file=sys.stderr)
            return 1
        return 0

    try:
        profile = loadProfile(args.profile)
    except (OSError, PdfImportError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    status = 0

    for path in args.pdf:
        base = os.path.splitext(os.path.basename(path))[0]
        trace = [] if args.trace else None
        try:
            lines = importPdf(path, profile, trace, args.skip_pages)
        except PdfImportError as e:
            print("error: %s: %s" % (path, e), file=sys.stderr)
            status = 1
            lines = None

        if trace is not None:
            tp = os.path.join(args.out, base + ".trace.tsv")
            writeTrace(trace, tp)
            print("trace: %s" % tp)

        if lines is None:
            continue

        sp = toScreenplay(lines)
        out = os.path.join(args.out, base + ".fountain")
        with open(out, "w", encoding="utf-8") as f:
            f.write(sp.generateFountain())

        counts = {}
        for ln in lines:
            if ln.lb == screenplay.LB_LAST:
                counts[TYPE_NAMES[ln.lt]] = counts.get(TYPE_NAMES[ln.lt], 0) + 1
        print("%s -> %s (%s)" % (path, out, ", ".join(
            "%d %s" % (n, k) for k, n in sorted(counts.items()))))

    return status


if __name__ == "__main__":
    sys.exit(main())
