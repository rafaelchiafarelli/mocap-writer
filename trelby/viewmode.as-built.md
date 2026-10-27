# viewmode.py — as built

`trelby/viewmode.py` (552 lines) decides where each script line is drawn on
screen and which line/column a mouse position points at. There are three
modes; the active one is `GlobalData.vm`, chosen by
`GlobalData.setViewMode` (`trelby/globaldata.py:106`) and saved in the
`state` file as `ViewMode` 0–2. `MyCtrl` calls it for painting, scrolling,
paging and hit testing; it draws nothing itself except in `drawTexts`.

## Classes

- `TextString(line, text, x, y, fi, isUnderlined)` (`trelby/viewmode.py:14`)
  — one piece of text at pixel `(x, y)` from the widget's top-left;
  `line` is the index in `Screenplay.lines`, or −1 for generated text
  (headers, `CONTINUED:`, `(MORE)`); `fi` is a `config.FontInfo`.
- `DisplayPage(pageNr, x1, y1, x2, y2)` (`trelby/viewmode.py:33`) — a page
  rectangle in pixels.
- `PageCache(ctrl)` (`trelby/viewmode.py:48`) — memoizes
  `generatePMLPage(pager, n, False, False)` during page-up scanning.
- `ViewMode` (`trelby/viewmode.py:67`) — abstract: `getScreen`,
  `getLineHeight`, `getPageWidth`, `drawTexts`, `pos2linecol`,
  `makeLineVisible`, `pageCmd`, plus the shared `*Generic` helpers
  (`trelby/viewmode.py:117-197`).
- `ViewModeDraft` (`trelby/viewmode.py:202`) — text only, one endless page.
- `ViewModeLayout` (`trelby/viewmode.py:280`) — real pages, stacked
  vertically, 10 px apart.
- `ViewModeSideBySide` (`trelby/viewmode.py:422`) — as many whole pages as
  fit, in one row; page up/down jumps a screenful of pages.

## Contract of `getScreen(ctrl, doExtra, partials=False, pageCache=None)`

Returns `(texts, dpages)` (`trelby/viewmode.py:69-82`):
- `texts`: `TextString`s with non-decreasing `line` (−1 entries aside);
  must contain at least one line;
- `dpages`: page rectangles, empty in draft mode;
- `doExtra`: as in `generatePMLPage` — include headers, `CONTINUED:` and
  styling (painting) or not (positions only);
- `partials`: include lines cut off at the bottom of the widget.

## How positions are computed

- **Draft** (`trelby/viewmode.py:204-255`): starts at `y = 15` px and the
  script's top line; each line adds `getSpacingBefore(i) / 10 * fontYdelta`
  then `fontYdelta` (`cfgGui.fontYdelta`: `cfgGl.fontYdelta`, default
  18 px, at the current zoom, `trelby/viewmode.py:215`). `x = centering
  offset + marginLeft * mm2p + (indent + paren extra) * fi.fx`, where `fi`
  is the screen font for the type's screen style (`cfgGui.tt2fi`). Text is
  upper-cased if the type's screen style says caps.
- **Layout** (`trelby/viewmode.py:282-397`): builds PML pages from the page
  containing the top line, with `generatePMLPage(..., forPDF=False,
  doExtra)`, and converts every `TextOp`'s millimeter position with
  `ctrl.mm2p`; the font is `cfgGui.fonts[op.flags & 3]`. The page holding
  the top line is shifted up so the top line sits at the top of the widget;
  the last page grows if text overflows it.
- **Side by side** (`trelby/viewmode.py:424-491`): same conversion, pages
  placed left to right at `pageGap + n * (pageW + pageGap)`.
- `getPageWidth` (layout and side by side, `trelby/viewmode.py:404-407`,
  `trelby/viewmode.py:498-501`; draft `trelby/viewmode.py:260-266`):
  `paperWidth / chX * fonts[NORMAL].fx` — page width in characters times the
  screen font's character width. `MyCtrl.refreshCache` derives `mm2p` from it
  (`trelby/trelbyctrl.py:114-117`).
- `getLineHeight`: `fontYdelta` in draft, `chY * mm2p + 1` otherwise
  (`trelby/viewmode.py:257-258`, `trelby/viewmode.py:399-402`).

## Scrolling and hit testing

- `pos2linecolGeneric` (`trelby/viewmode.py:117`): the last text line whose
  bottom is below `y`; column from `(x - t.x) / fi.fx`. Side by side has its
  own box test (`trelby/viewmode.py:503`).
- `makeLineVisibleGeneric` (`trelby/viewmode.py:141`): if
  `recenterOnScroll` is off and the move has a direction, scroll a few lines
  at a time (`jumpAhead` 1 in draft, 3 in layout) up to
  `MAX_JUMP_DISTANCE` = 17 (`trelby/viewmode.py:10`); otherwise put the line
  in the middle of the screen.
- `pageCmdGeneric` (`trelby/viewmode.py:168`): page down moves cursor and
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
  and handler in `MyFrame` (`trelby/trelbyframe.py:109-121`,
  `trelby/trelbyframe.py:797-833`), and widen the `ViewMode` range in
  `GlobalData` (`trelby/globaldata.py:62-68`).

## Gotchas

- Draft mode gives the "page" a width but no top or bottom; page breaks are
  drawn by `MyCtrl.OnPaint` as lines, not here.
- There is no horizontal scrolling: a page wider than the widget (a high
  zoom or a narrow window) is left-aligned and its right part is not shown,
  cursor included (`cox` clamped at 0, `trelby/viewmode.py:214`,
  `trelby/viewmode.py:298`). Bug: [bugs/editor/12](../initiatives/bugs/epics/editor/tasks/12-no-horizontal-scroll.md).
- `getScreen` is called several times per keystroke (`isLineVisible`,
  `makeLineVisible`, `OnPaint`), and in layout modes each call rebuilds PML
  pages; `PageCache` is only used for page-up scanning
  (`trelby/viewmode.py:180-187`).
- In layout and side-by-side modes the scene number counter starts from
  `getSceneNumber` of the first line on the page, but `sceneContNr`
  (`CONTINUED (2)`) is reset on every page, so screen and PDF can differ
  there (`trelby/viewmode.py:342-345`, `trelby/viewmode.py:455-458`). Bug: [bugs/editor/8](../initiatives/bugs/epics/editor/tasks/8-scene-cont-number.md).
- `ViewModeSideBySide.makeLineVisible` ignores direction and just sets the
  top line (`trelby/viewmode.py:539-540`). Bug: [bugs/editor/7](../initiatives/bugs/epics/editor/tasks/7-side-by-side-scroll.md).
- The abstract methods raise `Exception("… " + _("not implemented"))`
  (`trelby/viewmode.py:83-114`).

## Tests

- None. View modes need a wx widget; they are exercised only by running the
  program.
