# viewmode.py — as built

`trelby/viewmode.py` (552 lines) decides where each script line is drawn on
screen and which line/column a mouse position points at. There are three
modes; the active one is `GlobalData.vm`, chosen by
`GlobalData.setViewMode` (`trelby/globaldata.py:106`) and saved in the
`state` file as `ViewMode` 0–2. `MyCtrl` calls it for painting, scrolling,
paging and hit testing; it draws nothing itself except in `drawTexts`.

## Classes

- `TextString(line, text, x, y, fi, isUnderlined)` (`trelby/viewmode.py:18`)
  — one piece of text at pixel `(x, y)` from the widget's top-left;
  `line` is the index in `Screenplay.lines`, or −1 for generated text
  (headers, `CONTINUED:`, `(MORE)`); `fi` is a `config.FontInfo`.
- `DisplayPage(pageNr, x1, y1, x2, y2)` (`trelby/viewmode.py:41`) — a page
  rectangle in pixels.
- `PageCache(ctrl)` (`trelby/viewmode.py:56`) — memoizes
  `generatePMLPage(pager, n, False, False)` during page-up scanning.
- `ViewMode` (`trelby/viewmode.py:75`) — abstract: `getScreen`,
  `getLineHeight`, `getPageWidth`, `drawTexts`, `pos2linecol`,
  `makeLineVisible`, `pageCmd`, plus the shared `*Generic` helpers
  (`trelby/viewmode.py:140-220`).
- `ViewModeDraft` (`trelby/viewmode.py:225`) — text only, one endless page.
- `ViewModeLayout` (`trelby/viewmode.py:304`) — real pages, stacked
  vertically, 10 px apart.
- `ViewModeSideBySide` (`trelby/viewmode.py:448`) — as many whole pages as
  fit, in one row; page up/down jumps a screenful of pages.

## Contract of `getScreen(ctrl, doExtra, partials=False, pageCache=None)`

Returns `(texts, dpages)` (`trelby/viewmode.py:77-90`):
- `texts`: `TextString`s with non-decreasing `line` (−1 entries aside);
  must contain at least one line;
- `dpages`: page rectangles, empty in draft mode;
- `doExtra`: as in `generatePMLPage` — include headers, `CONTINUED:` and
  styling (painting) or not (positions only);
- `partials`: include lines cut off at the bottom of the widget.

## How positions are computed

- **Draft** (`trelby/viewmode.py:227-279`): starts at `y = 15` px and the
  script's top line; each line adds `getSpacingBefore(i) / 10 * fontYdelta`
  then `fontYdelta` (`cfgGui.fontYdelta`: `cfgGl.fontYdelta`, default
  18 px, at the current zoom, `trelby/viewmode.py:238`). `x = centering
  offset + marginLeft * mm2p + (indent + paren extra) * fi.fx`, where `fi`
  is the screen font for the type's screen style (`cfgGui.tt2fi`). Text is
  upper-cased if the type's screen style says caps. With `doExtra`, a
  scene heading's number label is drawn left of it, as a −1 `TextString`
  (`trelby/viewmode.py:244`, fountain-native/scenes/4).
- **Layout** (`trelby/viewmode.py:306-423`): builds PML pages from the page
  containing the top line, with `generatePMLPage(..., forPDF=False,
  doExtra)`, and converts every `TextOp`'s millimeter position with
  `ctrl.mm2p`; the font is `cfgGui.fonts[op.flags & 3]`. The page holding
  the top line is shifted up so the top line sits at the top of the widget;
  the last page grows if text overflows it.
- **Side by side** (`trelby/viewmode.py:450-518`): same conversion, pages
  placed left to right at `pageGap + n * (pageW + pageGap)`.
- `getPageWidth` (layout and side by side, `trelby/viewmode.py:430-433`,
  `trelby/viewmode.py:525-528`; draft `trelby/viewmode.py:284-290`):
  `paperWidth / chX * fonts[NORMAL].fx` — page width in characters times the
  screen font's character width. `MyCtrl.refreshCache` derives `mm2p` from it
  (`trelby/trelbyctrl.py:126-129`).
- `getLineHeight`: `fontYdelta` in draft, `chY * mm2p + 1` otherwise
  (`trelby/viewmode.py:281-282`, `trelby/viewmode.py:425-428`).

## Scrolling and hit testing

- `TextString.sceneLine` is the heading's line for a scene number's text,
  −1 otherwise; `sceneNumberAt(ctrl, x, y)` (`trelby/viewmode.py:126`)
  returns the heading whose number is at (x, y), from a `doExtra` screen
  (fountain-native/scenes/4).

- `pos2linecolGeneric` (`trelby/viewmode.py:140`): the last text line whose
  bottom is below `y`; column from `(x - t.x) / fi.fx`. Side by side has its
  own box test (`trelby/viewmode.py:530`).
- `makeLineVisibleGeneric` (`trelby/viewmode.py:164`): if
  `recenterOnScroll` is off and the move has a direction, scroll a few lines
  at a time (`jumpAhead` 1 in draft, 3 in layout) up to
  `MAX_JUMP_DISTANCE` = 17 (`trelby/viewmode.py:11`); otherwise put the line
  in the middle of the screen.
- `pageCmdGeneric` (`trelby/viewmode.py:191`): page down moves cursor and
  top line to the last visible line; page up walks the top line back one
  line at a time until the cursor would leave the screen.

## Extension points

- **Screen fonts / zoom**: every pixel size here comes from three inputs —
  the four screen fonts (`cfgGui.fonts`, from `ConfigGlobal.font*`), the
  draft line height `cfgGui.fontYdelta`, and `ctrl.mm2p` (from
  `getPageWidth`). The zoom scales the first two in `ConfigGui`; `mm2p`
  follows from the font width. Nothing here stores a zoom of its own.
- **Colors** are not used here; `MyCtrl.OnPaint` colors what `getScreen`
  returns.
- **A new view mode**: subclass `ViewMode`, implement the seven methods,
  add a `VIEWMODE_*` constant and instance in `GlobalData`
  (`trelby/globaldata.py:25-29`, `trelby/globaldata.py:79-83`), a menu item
  and handler in `MyFrame` (`trelby/trelbyframe.py:140-152`,
  `trelby/trelbyframe.py:1248-1284`), and widen the `ViewMode` range in
  `GlobalData` (`trelby/globaldata.py:62-68`).

## Gotchas

- Draft mode gives the "page" a width but no top or bottom; page breaks are
  drawn by `MyCtrl.OnPaint` as lines, not here.
- There is no horizontal scrolling: a page wider than the widget (a high
  zoom or a narrow window) is left-aligned and its right part is not shown,
  cursor included (`cox` clamped at 0, `trelby/viewmode.py:237`,
  `trelby/viewmode.py:322`). Bug: [bugs/editor/12](../initiatives/bugs/epics/editor/tasks/12-no-horizontal-scroll.md).
- `getScreen` is called several times per keystroke (`isLineVisible`,
  `makeLineVisible`, `OnPaint`), and in layout modes each call rebuilds PML
  pages; `PageCache` is only used for page-up scanning
  (`trelby/viewmode.py:203-210`).
- In layout and side-by-side modes the pager gets the scene number labels
  (`scenenumbers.labels`) and the label of the scene holding the line
  before the page (`trelby/viewmode.py:329`, `trelby/viewmode.py:472`), and `sceneContNr`
  (`CONTINUED (2)`) from `Screenplay.sceneContNrAt(pageNr)`, the number the
  PDF has there (`trelby/viewmode.py:370`, `trelby/viewmode.py:484`,
  `trelby/screenplay.py:1591`).
- `ViewModeSideBySide.makeLineVisible` (`trelby/viewmode.py:576`) moves by
  whole pages: scrolling down makes the line's page the last one shown,
  up the first, otherwise (or with `recenterOnScroll`) the middle one;
  `pageCount` is how many pages fit (`trelby/viewmode.py:567`).
- The abstract methods raise `Exception("… " + _("not implemented"))`
  (`trelby/viewmode.py:91-122`).

## Tests

- None. View modes need a wx widget; they are exercised only by running the
  program.
