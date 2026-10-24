# PDF import: a master-scene screenplay PDF with selectable text becomes a
# list of Lines, each line classified by its position on the page. The
# layout (where scene headings, action, character cues, parentheticals,
# dialogue and transitions sit) is detected from the PDF itself
# (detectLayout), deterministically and without an LLM; a TOML layout
# profile can be given instead (trelby/pdfprofiles/CLAUDE.md).
#
# Nothing stops the import: anything doubtful is read as well as possible and
# reported as an issue, which also becomes an "IMPORT:" Note element just
# before the text it is about, saying what is wrong and how to fix it. With
# strict=True (CLI --strict) the first unreadable line stops the import.
#
# Command line (writes one .fountain per PDF):
#   python -m trelby.pdfimport import <pdf>... --out <dir> [--profile <toml>]
#   python -m trelby.pdfimport probe <pdf>

import argparse
import collections
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

# pseudo-element: scene heading if the line starts like one (the profile's
# scene_prefixes, or SCENE_RE for a detected layout), action otherwise
# (master-scene scripts share that indent)
SCENE_ACTION = "scene_action"

# names used in traces and messages
TYPE_NAMES = {v: k for k, v in ELEMENTS.items()}

# how a scene heading starts, after an optional typed scene number:
# INT. / EXT. / INT./EXT. / I/E / EST., also without the dot ("INT NAVE")
SCENE_RE = re.compile(
    r"^(?:(\d+[A-Z]*)\.?\s+)?"
    r"(INT\.?\s*/\s*EXT|EXT\.?\s*/\s*INT|INT|EXT|EST|I\s*/\s*E)"
    r"(\.|\s|-|/|$)"
)

NUMBER_RE = re.compile(r"^\d+[A-Z]*\.?$")

# page furniture every screenplay program writes; dropped in every layout
STANDARD_DROPS = [
    r"(?i)^\((MORE|MAIS|CONTINUA)\)$",
    r"(?i)^\(?CONTINUED\)?:?$",
    r"(?i)^\(?CONTINUA(ÇÃO|CAO|NDO)?\)?:?$",
]

# cut from the end of character names
STANDARD_SUFFIXES = [
    r"(?i)\s*\((CONT['’]D|CONT\.?|CONTINUED|CONTINUANDO|CONTINUA|CONT\.\s*D)\)$",
]

NOTE_PREFIX = "IMPORT: "


class PdfImportError(Exception):
    def __init__(self, msg, page=None, lineNo=None):
        Exception.__init__(self, msg)
        self.page = page
        self.lineNo = lineNo


@dataclass
class Issue:
    page: int
    lineNo: int
    message: str

    def __str__(self):
        return "page %d, line %d: %s" % (self.page, self.lineNo, self.message)


@dataclass
class Rule:
    element: str
    # exactly one of x (left edge), x1 (right edge), xc (center) is set
    edge: str
    pos: float
    tolerance: float

    def matches(self, seg):
        return abs(seg.edgePos(self.edge) - self.pos) <= self.tolerance

    def distance(self, seg):
        return abs(seg.edgePos(self.edge) - self.pos)

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
    sceneNumberInline: Optional[re.Pattern]
    # detected layouts: scene headings recognized by SCENE_RE instead of
    # scenePrefixes, and an upper-case line with a typed scene number but no
    # INT./EXT. is a scene heading (reported as an issue)
    sceneRe: Optional[re.Pattern] = None
    numberedUpperIsScene: bool = False
    # what detectLayout found, for the report and probe
    summary: List[str] = field(default_factory=list)


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
SCENE_NUMBER_KEYS = {"left", "right", "tolerance", "pattern", "inline"}


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
        sceneNumberInline=re.compile(sn["inline"]) if "inline" in sn else None,
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


def _isUpper(text):
    return any(c.isalpha() for c in text) and text == text.upper()


# the most common value of xs after merging values within tol of each
# other; (value, count) or (None, 0)
def _mode(xs, tol=2.0):
    if not xs:
        return None, 0
    counts = collections.Counter(round(x, 1) for x in xs)
    best, bestN = None, 0
    for x in counts:
        n = sum(c for y, c in counts.items() if abs(y - x) <= tol)
        if n > bestN or (n == bestN and counts[x] > counts.get(best, 0)):
            best, bestN = x, n
    return best, bestN


# a layout Profile worked out from the PDF itself, plus the issues found
# while doing it. Deterministic: the same PDF always gives the same layout.
def detectLayout(pages, name="detected"):
    issues = []
    summary = []
    tol = 3.0
    segmentGap = 28.0

    # 1. title page: a first page with no scene heading and few lines
    skip = 0
    if len(pages) > 1:
        pn, h, lines = pages[0]
        if len(lines) <= 20 and not any(SCENE_RE.match(ln.text.upper()) for ln in lines):
            skip = 1
            issues.append(Issue(1, 1, "page 1 looks like a title page and was not "
                                "imported; put the title in Script > Title pages"))
            summary.append("title page: page 1 (skipped)")

    body = [(pn, h, lines) for pn, h, lines in pages if pn > skip]

    # 2. page numbers: a lone number as the first or last line of a page
    firstTops, lastTops = [], []
    for pn, h, lines in body:
        if lines and NUMBER_RE.match(lines[0].text):
            firstTops.append(lines[0].top)
        if len(lines) > 1 and NUMBER_RE.match(lines[-1].text):
            lastTops.append(lines[-1].top)

    furniture = [Furniture(re.compile(p), None, None) for p in STANDARD_DROPS]
    if firstTops:
        furniture.append(Furniture(NUMBER_RE, None, max(firstTops) + 1.0))
        summary.append("page numbers: top of page (top <= %.1f)" % max(firstTops))
    if lastTops:
        furniture.append(Furniture(NUMBER_RE, min(lastTops) - 1.0, None))
        summary.append("page numbers: bottom of page (top >= %.1f)" % min(lastTops))

    def isFurniture(ln):
        return any(f.matches(ln.text.strip(), ln.top) for f in furniture)

    # 3. margin scene numbers ("12   INT. ..." / "INT. ...   12") and the
    # single-column lines everything else is measured on
    snLeft, snRight = [], []
    single = []  # (page, index in page, PdfLine, Segment)
    for pn, h, lines in body:
        for i, ln in enumerate(lines):
            if isFurniture(ln):
                continue
            ws = ln.words
            if len(ws) >= 3 and NUMBER_RE.match(ws[0].text) and ws[1].x0 - ws[0].x1 > 10.0 \
                    and SCENE_RE.match(" ".join(w.text for w in ws[1:]).upper()):
                snLeft.append(ws[0].x0)
                ws = ws[1:]
            if len(ws) >= 3 and NUMBER_RE.match(ws[-1].text) and ws[-1].x0 - ws[-2].x1 > 10.0 \
                    and SCENE_RE.match(" ".join(w.text for w in ws[:-1]).upper()):
                snRight.append(ws[-1].x0)
                ws = ws[:-1]
            segs = _split(ws, segmentGap)
            if len(segs) == 1:
                single.append((pn, i, ln, segs[0]))

    # 4. scene headings and the action indent
    sceneXs = [seg.x0 for pn, i, ln, seg in single if SCENE_RE.match(seg.text.upper())]
    actionX, nScenes = _mode(sceneXs)
    if actionX is None:
        # no scene headings: the leftmost indent holding a tenth of the text
        xs = sorted(collections.Counter(round(seg.x0) for _p, _i, _l, seg in single).items())
        total = sum(n for _x, n in xs) or 1
        actionX = next((float(x) for x, n in xs if n >= total / 10.0), xs[0][0] if xs else 72.0)
        issues.append(Issue(skip + 1, 1, "no scene heading (INT./EXT.) found; "
                            "every line at the left margin is read as action"))
    summary.append("scene headings / action: x = %.1f (%d headings)" % (actionX, nScenes))

    inlineNumbered = sum(
        1 for _p, _i, _l, seg in single
        if (m := SCENE_RE.match(seg.text.upper())) and m.group(1)
    )

    # 5. character cues: short upper-case lines right of the action indent,
    # followed at once (no blank line) by more text
    steps = []
    byPage = collections.defaultdict(list)
    for pn, i, ln, seg in single:
        byPage[pn].append((ln, seg))
    for pn in byPage:
        rows = byPage[pn]
        for a, b in zip(rows, rows[1:]):
            d = b[0].top - a[0].top
            if d > 0:
                steps.append(d)
    # the line step is the smallest common step (a tenth of all steps or
    # more), not the most common one: where most speeches are one line long,
    # blank-line steps outnumber line steps
    stepCounts = collections.Counter(round(d * 2) / 2 for d in steps)
    common = [d for d, n in stepCounts.items() if n >= 0.1 * len(steps)]
    lineStep = min(common) if common else 12.0

    cues = []  # (page, rows, index)
    for pn, rows in byPage.items():
        for k, (ln, seg) in enumerate(rows):
            t = seg.text
            if seg.x0 > actionX + 15 and _isUpper(t) and len(t) <= 50 \
                    and not t.endswith(":") and not t.startswith("(") \
                    and not SCENE_RE.match(t.upper()) \
                    and k + 1 < len(rows) and rows[k + 1][0].top - ln.top <= lineStep * 1.5:
                cues.append((pn, rows, k))

    rules = [Rule(SCENE_ACTION, "x", actionX, tol)]
    charX, nChar = _mode([rows[k][1].x0 for pn, rows, k in cues])
    charRule = None
    if charX is not None:
        if nChar >= 0.6 * len(cues):
            charRule = Rule("character", "x", charX, tol)
        else:
            # names centered, not aligned: match their centers
            cx, _n = _mode([rows[k][1].edgePos("xc") for pn, rows, k in cues], 4.0)
            charRule = Rule("character", "xc", cx, 4.0)
        cues = [(pn, rows, k) for pn, rows, k in cues if charRule.matches(rows[k][1])]
        summary.append("character cues: %s (%d)" % (charRule.describe(), len(cues)))

    # 6. dialogue and parentheticals: what follows a cue
    diaXs, parXs = [], []
    for pn, rows, k in cues:
        prevTop = rows[k][0].top
        for ln, seg in rows[k + 1:]:
            if ln.top - prevTop > lineStep * 1.5 or charRule.matches(seg) and _isUpper(seg.text):
                break
            prevTop = ln.top
            (parXs if seg.text.startswith("(") else diaXs).append(seg.x0)

    diaX, _n = _mode(diaXs)
    parX, nPar = _mode(parXs)
    if diaX is not None and abs(diaX - actionX) > tol:
        rules.append(Rule("dialogue", "x", diaX, tol))
        summary.append("dialogue: x = %.1f" % diaX)
    elif cues:
        issues.append(Issue(skip + 1, 1, "speeches are at the action indent; they "
                            "are read as action — mark them as Dialogue"))
    if parX is not None and nPar >= 1 and all(abs(parX - r.pos) > tol for r in rules):
        rules.append(Rule("parenthetical", "x", parX, tol))
        summary.append("parentheticals: x = %.1f" % parX)
    if charRule is not None:
        rules.append(charRule)
    elif not cues:
        issues.append(Issue(skip + 1, 1, "no character cues found; check that the "
                            "PDF is a screenplay"))

    # 7. transitions: upper-case lines ending in ":" (or FADE OUT.) right of
    # the action indent, at no other indent
    trans = [
        seg for _p, _i, _l, seg in single
        if seg.x0 > actionX + 15 and _isUpper(seg.text)
        and (seg.text.endswith(":") or re.match(r"(?i)^FADE (OUT|TO BLACK)", seg.text))
        and not any(r.matches(seg) for r in rules)
    ]
    if trans:
        tx, n = _mode([s.x0 for s in trans])
        if n >= 0.7 * len(trans):
            rules.append(Rule("transition", "x", tx, tol))
        else:
            tx1, _n = _mode([s.x1 for s in trans])
            rules.append(Rule("transition", "x1", tx1, tol))
        summary.append("transitions: %s" % rules[-1].describe())

    # 8. dual dialogue: two short upper-case columns on one line
    dualLeft, dualRight = [], []
    leftC, rightC, leftD, rightD, leftP, rightP = [], [], [], [], [], []
    for pn, h, lines in body:
        k = 0
        while k < len(lines):
            segs = _split(lines[k].words, segmentGap)
            if len(segs) == 2 and all(_isUpper(s.text) and len(s.text) <= 40 for s in segs) \
                    and not isFurniture(lines[k]):
                leftC.append(segs[0].x0)
                rightC.append(segs[1].x0)
                mid = (segs[0].x1 + segs[1].x0) / 2.0
                prevTop = lines[k].top
                k += 1
                while k < len(lines) and lines[k].top - prevTop <= lineStep * 1.5:
                    for s in _split(lines[k].words, segmentGap):
                        left = s.x0 < mid
                        if s.text.startswith("("):
                            (leftP if left else rightP).append(s.x0)
                        else:
                            (leftD if left else rightD).append(s.x0)
                    prevTop = lines[k].top
                    k += 1
                continue
            k += 1
    if leftC:
        for out, xs, el in ((dualLeft, leftC, "character"), (dualLeft, leftP, "parenthetical"),
                            (dualLeft, leftD, "dialogue"), (dualRight, rightC, "character"),
                            (dualRight, rightP, "parenthetical"), (dualRight, rightD, "dialogue")):
            x, _n = _mode(xs)
            if x is not None:
                out.append(Rule(el, "x", x, tol))
        summary.append("dual dialogue: %d blocks" % len(leftC))

    snL = _mode(snLeft)[0]
    snR = _mode(snRight)[0]
    if snL is not None or snR is not None:
        summary.append("margin scene numbers: %s" % ", ".join(
            "%s x = %.1f" % (side, x) for side, x in (("left", snL), ("right", snR)) if x is not None))
    if inlineNumbered:
        summary.append("scene numbers typed in the heading: %d" % inlineNumbered)

    profile = Profile(
        name=name,
        tolerance=tol,
        segmentGap=segmentGap,
        paragraphGap=lineStep * 1.5,
        skipPages=skip,
        scenePrefixes=[],
        rules=rules,
        dualLeft=dualLeft,
        dualRight=dualRight,
        furniture=furniture,
        characterSuffixes=[re.compile(p) for p in STANDARD_SUFFIXES],
        sceneNumberPattern=NUMBER_RE if (snL is not None or snR is not None) else None,
        sceneNumberLeft=Rule("scene", "x", snL, tol) if snL is not None else None,
        sceneNumberRight=Rule("scene", "x", snR, tol) if snR is not None else None,
        sceneNumberInline=re.compile(r"^(\d+[A-Z]*)\.?\s+"),
        sceneRe=SCENE_RE,
        numberedUpperIsScene=inlineNumbered >= 3,
        summary=summary,
    )
    return profile, issues


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
    lineNo: int = 0
    issues: List[Issue] = field(default_factory=list)


def _hasScenePrefix(text, profile):
    up = text.upper()
    if profile.sceneRe is not None:
        return bool(profile.sceneRe.match(up))
    return any(up.startswith(p) for p in profile.scenePrefixes)


# a scene number written at the start of a heading ("12. INT. ..."), by the
# profile's [scene_numbers] inline regex (group 1 = the number). Returns
# (number, rest) or (None, text); with requirePrefix, only when the rest
# starts with a scene prefix.
def _inlineNumber(text, profile, requirePrefix):
    if profile.sceneNumberInline is None:
        return None, text
    m = profile.sceneNumberInline.match(text)
    if not m:
        return None, text
    rest = text[m.end():]
    if requirePrefix and not _hasScenePrefix(rest, profile):
        return None, text
    return m.group(1), rest


# (line type, rule, text, inline scene number, issue message or None) of a
# segment, or (None, None, text, None, None) if no rule matches.
def _classify(seg, rules, profile):
    text = seg.text
    for r in rules:
        if r.matches(seg):
            el = r.element
            if el == SCENE_ACTION:
                num, rest = _inlineNumber(text, profile, True)
                if num is not None:
                    return screenplay.SCENE, r, rest, num, None
                if _hasScenePrefix(text, profile):
                    return screenplay.SCENE, r, text, None, None
                num, rest = _inlineNumber(text, profile, False)
                if num is not None and profile.numberedUpperIsScene and _isUpper(rest):
                    return (screenplay.SCENE, r, rest, num,
                            "scene heading %s has no INT./EXT.; add it" % num)
                return screenplay.ACTION, r, text, None, None
            if el == "scene":
                num, rest = _inlineNumber(text, profile, False)
                return screenplay.SCENE, r, rest, num, None
            return ELEMENTS[el], r, text, None, None
    return None, None, text, None, None


# the nearest rule to a segment no rule matches (lenient reading)
def _nearest(seg, rules):
    return min(rules, key=lambda r: r.distance(seg)) if rules else None


# classify every line of the PDF; returns a list of _Item.
def _items(pages, profile, trace, skipPages, strict):
    items = []
    dualBlocks = 0
    inDual = False
    prevTop = None

    def fail(ln, msg):
        raise PdfImportError("page %d, line %d: %s" % (ln.page, ln.lineNo, msg), ln.page, ln.lineNo)

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
            lineIssues = []

            if inDual and gap is not None and gap > profile.paragraphGap:
                inDual = False

            if len(segs) == 2 and not inDual:
                # a dual-dialogue block starts with two character names
                lt0 = _classify(segs[0], profile.dualLeft, profile)[0]
                lt1 = _classify(segs[1], profile.dualRight, profile)[0]
                if lt0 == screenplay.CHARACTER and lt1 == screenplay.CHARACTER:
                    inDual = True
                    dualBlocks += 1

            if len(segs) >= 2 and not inDual:
                msg = "text in %d columns (x0 %s) read as one line" % (
                    len(segs), ", ".join("%.1f" % s.x0 for s in segs))
                if strict:
                    fail(ln, "%s: %r" % (msg, ln.text))
                lineIssues.append(Issue(ln.page, ln.lineNo, msg + "; check its type"))
                segs = [Segment(words)]

            if inDual:
                if len(segs) > 2:
                    if strict:
                        fail(ln, "%d text columns in dual dialogue: %r" % (len(segs), ln.text))
                    segs = [segs[0], Segment([w for s in segs[1:] for w in s.words])]

                for seg in segs:
                    lt, r, col = None, None, None
                    for col, rules in (("left", profile.dualLeft), ("right", profile.dualRight)):
                        lt, r, _text, _num, _msg = _classify(seg, rules, profile)
                        if lt is not None:
                            break
                    segIssues = list(lineIssues)
                    if lt is None:
                        if strict:
                            fail(ln, "x0 %.1f matches no dual-dialogue column rule: %r"
                                 % (seg.x0, seg.text))
                        r = _nearest(seg, profile.dualLeft + profile.dualRight)
                        col = "left" if r in profile.dualLeft else "right"
                        lt = ELEMENTS[r.element]
                        segIssues.append(Issue(ln.page, ln.lineNo,
                            "dual dialogue text at an unusual position (x0 %.1f) read "
                            "as %s; check it" % (seg.x0, TYPE_NAMES[lt])))
                    trace.add(ln, seg, "dual %s %s" % (col, TYPE_NAMES[lt]), r.describe())
                    items.append(_Item(lt, seg.text, ln.page, ln.top, col, dualBlocks,
                                       ln.lineNo, segIssues))
                continue

            seg = segs[0]
            lt, r, text, num, msg = _classify(seg, profile.rules, profile)
            if lt is None:
                if strict:
                    trace.add(ln, seg, "UNKNOWN INDENT")
                    fail(ln, "indent x0 %.1f (right edge %.1f) matches no rule of "
                         "profile %r: %r" % (seg.x0, seg.x1, profile.name, seg.text))
                r = _nearest(seg, profile.rules)
                el = r.element
                if el == SCENE_ACTION:
                    el = "scene" if _hasScenePrefix(text, profile) else "action"
                lt = ELEMENTS[el]
                lineIssues.append(Issue(ln.page, ln.lineNo,
                    "unusual indent (x0 %.1f) read as %s; if that is wrong, change "
                    "the element type" % (seg.x0, el)))
                trace.add(ln, seg, "%s (nearest)" % el, r.describe())
            else:
                trace.add(ln, seg, TYPE_NAMES[lt], r.describe())

            if msg:
                lineIssues.append(Issue(ln.page, ln.lineNo, msg))

            num = ln.sceneNumber or num
            if lt == screenplay.SCENE and num:
                text += " #%s#" % num

            items.append(_Item(lt, text, ln.page, ln.top, lineNo=ln.lineNo, issues=lineIssues))

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


# group items into elements: [lt, [texts], first item, [items]].
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
            elems.append([it.lt, [it.text], it, [it]])
            if it.column is not None:
                prevByColumn[(it.dualBlock, it.column, "elem")] = elems[-1]
        else:
            e = elems[-1] if it.column is None else prevByColumn[(it.dualBlock, it.column, "elem")]
            e[1].append(it.text)
            e[3].append(it)

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

    return out


# likely mistakes in the PDF itself, added to the issues of the element
# they are about: a character cue with no parenthetical or dialogue after it
# (usually a speech typed at the action indent).
def _checkElements(elems):
    for i, (lt, texts, it, its) in enumerate(elems):
        if lt != screenplay.CHARACTER:
            continue
        nxt = elems[i + 1][0] if i + 1 < len(elems) else None
        if nxt not in (screenplay.PAREN, screenplay.DIALOGUE):
            what = TYPE_NAMES.get(nxt, "the end of the script")
            it.issues.append(Issue(it.page, it.lineNo,
                "character %s is followed by %s, not a speech; if the next "
                "paragraph is the speech, change it to Dialogue" % (texts[0], what)))


def _noteText(issue):
    return "%s%s (PDF page %d, line %d)" % (NOTE_PREFIX, issue.message, issue.page, issue.lineNo)


# import a PDF; returns a list of Lines that meets the importer contract
# (trelby/myimport.as-built.md).
# - profile: a Profile, or None to detect the layout from the PDF
# - trace: if a list, receives one dict per piece of text with the decision
#   taken for it, and an ISSUE row per issue
# - issues: if a list, receives every Issue, in script order
# - notes: put each issue in the script as an "IMPORT:" Note element before
#   the element it is about
# - strict: stop at the first line no rule covers (PdfImportError)
# - layout: if a list, receives the detected layout's summary lines
def importPdf(path, profile=None, trace=None, skipPages=None, issues=None,
              notes=True, strict=False, layout=None):
    pages = extractPages(path)

    found = []
    if profile is None:
        profile, found = detectLayout(pages, os.path.splitext(os.path.basename(path))[0])
        if layout is not None:
            layout.extend(profile.summary)

    if skipPages is None:
        skipPages = profile.skipPages

    items = _items(pages, profile, _Trace(trace), skipPages, strict)
    elems = _elements(items, profile)
    _checkElements(elems)

    allIssues = list(found)
    ret = []

    def addNote(iss):
        ret.append(Line(screenplay.LB_LAST, screenplay.NOTE, _noteText(iss)))

    if notes:
        for iss in found:
            addNote(iss)

    for lt, texts, _it, its in elems:
        here = [iss for it in its for iss in it.issues]
        allIssues.extend(here)
        if notes:
            for iss in here:
                addNote(iss)
        for t in texts:
            ret.append(Line(screenplay.LB_SPACE, lt, t))
        ret[-1].lb = screenplay.LB_LAST

    if not any(ln.lt != screenplay.NOTE for ln in ret):
        raise PdfImportError("%s: no text found (a scanned PDF?)" % path)

    if issues is not None:
        issues.extend(allIssues)
    if trace is not None:
        for iss in allIssues:
            trace.append({"page": iss.page, "line": iss.lineNo, "top": "", "x0": "",
                          "x1": "", "decision": "ISSUE", "rule": "", "text": iss.message})

    return ret


# the indents found in a PDF and the layout detectLayout makes of them, for
# checking a detection or writing a profile. Returns text.
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

    profile, issues = detectLayout(pages)
    out.append("")
    out.append("detected layout:")
    out.extend("  " + s for s in profile.summary)
    out.extend("  issue: %s" % i for i in issues)
    return "\n".join(out)


def writeTrace(trace, path):
    cols = ["page", "line", "top", "x0", "x1", "decision", "rule", "text"]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in trace:
            f.write("\t".join(str(r[c]).replace("\t", " ") for c in cols) + "\n")


# the import report shown after File > Import: the layout found and every
# issue, each also in the script as an IMPORT: note.
def report(path, layout, issues):
    out = [os.path.basename(path), ""]
    if layout:
        out.append("Layout found in the PDF:")
        out.extend("  " + s for s in layout)
        out.append("")
    if issues:
        out.append("%d issue(s), each also written in the script as a note "
                   "starting with \"%s\" just before the text it is about. Fix "
                   "the text, then delete the note." % (len(issues), NOTE_PREFIX.strip()))
        out.append("")
        out.extend("- %s" % i for i in issues)
    else:
        out.append("No issues.")
    return "\n".join(out)


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
    imp.add_argument("--out", required=True, help="output directory")
    imp.add_argument("--profile", help="layout profile (default: detect the layout)")
    imp.add_argument("--skip-pages", type=int, default=None,
                     help="leading pages to skip (default: detected, or the profile's skip_pages)")
    imp.add_argument("--strict", action="store_true",
                     help="stop at the first line no rule covers")
    imp.add_argument("--no-notes", action="store_true",
                     help="do not write IMPORT: notes into the script")
    imp.add_argument("--trace", action="store_true",
                     help="also write <name>.trace.tsv: every piece of text and its decision")

    pr = sub.add_parser("probe", help="the indents in a PDF and the layout detected")
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

    profile = None
    if args.profile:
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
        issues = []
        layout = []
        try:
            lines = importPdf(path, profile, trace, args.skip_pages, issues,
                              not args.no_notes, args.strict, layout)
        except PdfImportError as e:
            print("error: %s: %s" % (path, e), file=sys.stderr)
            status = 1
            lines = None

        if trace is not None:
            tp = os.path.join(args.out, base + ".trace.tsv")
            writeTrace(trace, tp)
            print("trace: %s" % tp)

        for s in layout:
            print("  layout: %s" % s)
        for iss in issues:
            print("issue: %s: %s" % (path, iss), file=sys.stderr)

        if lines is None:
            continue

        sp = toScreenplay(lines)
        out = os.path.join(args.out, base + ".fountain")
        with open(out, "w", encoding="utf-8") as f:
            f.write(sp.generateFountain())

        counts = {}
        for ln in lines:
            if ln.lb == screenplay.LB_LAST and ln.lt != screenplay.NOTE:
                counts[TYPE_NAMES[ln.lt]] = counts.get(TYPE_NAMES[ln.lt], 0) + 1
        print("%s -> %s (%s; %d issues)" % (path, out, ", ".join(
            "%d %s" % (n, k) for k, n in sorted(counts.items())), len(issues)))

    return status


if __name__ == "__main__":
    sys.exit(main())
