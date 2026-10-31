# viewmode.py — as built

`trelby/viewmode.py` (643 lines) decides where each script line is drawn on
screen and which line/column a mouse position points at. There are three
modes; the active one is `GlobalData.vm`, chosen by
`GlobalData.setViewMode` (`trelby/globaldata.py:106`) and saved in the
`state` file as `ViewMode` 0–2. `MyCtrl` calls it for painting, scrolling,
paging and hit testing; it draws nothing itself except in `drawTexts`.

## Classes

- `TextString(line, text, x, y, fi, isUnderlined)` (`trelby/viewmode.py:281`)
  — one piece of text at pixel `(x, y)` from the widget's top-left;
  `line` is the index in `Screenplay.lines`, or −1 for generated text
  (headers, `CONTINUED:`, `(MORE)`); `fi` is a `config.FontInfo`.
- `DisplayPage(pageNr, x1, y1, x2, y2)` (`trelby/viewmode.py:73`) — a page
  rectangle in pixels.
- `PageCache(ctrl)` (`trelby/viewmode.py:88`) — memoizes
  `generatePMLPage(pager, n, False, False)` during page-up scanning.
- `ViewMode` (`trelby/viewmode.py:107`) — abstract: `getScreen`,
  `getLineHeight`, `getPageWidth`, `drawTexts`, `pos2linecol`,
  `makeLineVisible`, `pageCmd`, plus the shared `*Generic` helpers
  (`trelby/viewmode.py:177-257`).
- `ViewModeDraft` (`trelby/viewmode.py:262`) — text only, one endless page.
- `ViewModeLayout` (`trelby/viewmode.py:341`) — real pages, stacked
  vertically, 10 px apart.
- `ViewModeSideBySide` (`trelby/viewmode.py:485`) — as many whole pages as
  fit, in one row; page up/down jumps a screenful of pages.

## Contract of `getScreen(ctrl, doExtra, partials=False, pageCache=None)`

Returns `(texts, dpages)` (`trelby/viewmode.py:109-122`):
- `texts`: `TextString`s with non-decreasing `line` (−1 entries aside);
  must contain at least one line;
- `dpages`: page rectangles, empty in draft mode;
- `doExtra`: as in `generatePMLPage` — include headers, `CONTINUED:` and
  styling (painting) or not (positions only);
- `partials`: include lines cut off at the bottom of the widget.

## How positions are computed

- **Draft** (`trelby/viewmode.py:264-316`): starts at `y = 15` px and the
  script's top line; each line adds `getSpacingBefore(i) / 10 * fontYdelta`
  then `fontYdelta` (`cfgGui.fontYdelta`: `cfgGl.fontYdelta`, default
  18 px, at the current zoom, `trelby/viewmode.py:275`). `x = page left
  (`contentLeft`, see below) + marginLeft * mm2p + (indent + paren extra) * fi.fx`, where `fi`
  is the screen font for the type's screen style (`cfgGui.tt2fi`). Text is
  upper-cased if the type's screen style says caps. With `doExtra`, a
  scene heading's number label is drawn left of it, as a −1 `TextString`
  (`trelby/viewmode.py:50`, fountain-native/scenes/4).
- **Layout** (`trelby/viewmode.py:343-460`): builds PML pages from the page
  containing the top line, with `generatePMLPage(..., forPDF=False,
  doExtra)`, and converts every `TextOp`'s millimeter position with
  `ctrl.mm2p`; the font is `cfgGui.fonts[op.flags & 3]`. The page holding
  the top line is shifted up so the top line sits at the top of the widget;
  the last page grows if text overflows it.
- **Side by side** (`trelby/viewmode.py:487-558`): same conversion, pages
  placed left to right at `pageGap + n * (pageW + pageGap)`, moved left by
  the horizontal scroll when one page is wider than the widget
  (`trelby/viewmode.py:517`).
- **Horizontal scroll** (bugs/editor/12): `contentLeft(width, contentW,
  hOffset)` (`trelby/viewmode.py:29`) centers a page that fits and puts
  one wider than the widget at `-hOffset`, kept by `clampOffset` within
  the page (`trelby/viewmode.py:23`); draft and layout place the page with
  it (`trelby/viewmode.py:274`, `trelby/viewmode.py:359`).
  `getContentWidth(ctrl)` is `pageW`, side by side `pageW + 2 *
  SBS_PAGE_GAP` (`trelby/viewmode.py:135`, `trelby/viewmode.py:607`).
  `followOffset(hOffset, x, w, width, contentW)` → the scroll that shows
  the cursor `H_MARGIN` (40 px) inside the edges (`trelby/viewmode.py:38`);
  `MyCtrl` holds `hOffset` and calls it.
- `getPageWidth` (layout and side by side, `trelby/viewmode.py:467-470`,
  `trelby/viewmode.py:565-568`; draft `trelby/viewmode.py:321-327`):
  `paperWidth / chX * fonts[NORMAL].fx` — page width in characters times the
  screen font's character width. `MyCtrl.refreshCache` derives `mm2p` from it
  (`trelby/trelbyctrl.py:132-135`).
- `getLineHeight`: `fontYdelta` in draft, `chY * mm2p + 1` otherwise
  (`trelby/viewmode.py:318-319`, `trelby/viewmode.py:462-465`).

## Scrolling and hit testing

- `TextString.sceneLine` is the heading's line for a scene number's text,
  −1 otherwise; `sceneNumberAt(ctrl, x, y)` (`trelby/viewmode.py:163`)
  returns the heading whose number is at (x, y), from a `doExtra` screen
  (fountain-native/scenes/4).

- `pos2linecolGeneric` (`trelby/viewmode.py:177`): the last text line whose
  bottom is below `y`; column from `(x - t.x) / fi.fx`. Side by side has its
  own box test (`trelby/viewmode.py:570`).
- `makeLineVisibleGeneric` (`trelby/viewmode.py:201`): if
  `recenterOnScroll` is off and the move has a direction, scroll a few lines
  at a time (`jumpAhead` 1 in draft, 3 in layout) up to
  `MAX_JUMP_DISTANCE` = 17 (`trelby/viewmode.py:11`); otherwise put the line
  in the middle of the screen.
- `pageCmdGeneric` (`trelby/viewmode.py:228`): page down moves cursor and
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
  and handler in `MyFrame` (`trelby/trelbyframe.py:147-159`,
  `trelby/trelbyframe.py:1448-1484`), and widen the `ViewMode` range in
  `GlobalData` (`trelby/globaldata.py:62-68`).

## Gotchas

- Draft mode gives the "page" a width but no top or bottom; page breaks are
  drawn by `MyCtrl.OnPaint` as lines, not here.
- The horizontal scroll follows the cursor only when the cursor moves
  (`MyCtrl.makeLineVisible`); scrolled away with the bar or the wheel, the
  cursor stays off screen until the next key.
- `getScreen` is called several times per keystroke (`isLineVisible`,
  `makeLineVisible`, `OnPaint`), and in layout modes each call rebuilds PML
  pages; `PageCache` is only used for page-up scanning
  (`trelby/viewmode.py:240-247`).
- In layout and side-by-side modes the pager gets the scene number labels
  (`scenenumbers.labels`) and the label of the scene holding the line
  before the page (`trelby/viewmode.py:366`, `trelby/viewmode.py:509`), and `sceneContNr`
  (`CONTINUED (2)`) from `Screenplay.sceneContNrAt(pageNr)`, the number the
  PDF has there (`trelby/viewmode.py:407`, `trelby/viewmode.py:524`,
  `trelby/screenplay.py:1598`).
- `ViewModeSideBySide.makeLineVisible` (`trelby/viewmode.py:619`) moves by
  whole pages: scrolling down makes the line's page the last one shown,
  up the first, otherwise (or with `recenterOnScroll`) the middle one;
  `pageCount` is how many pages fit (`trelby/viewmode.py:610`).
- The abstract methods raise `Exception("… " + _("not implemented"))`
  (`trelby/viewmode.py:123-159`).

## Tests

- None. View modes need a wx widget; they are exercised only by running the
  program.
