# media — source artwork

**Role:** The editable source of the splash image.
**Entry points:** none; open in an SVG editor (Inkscape).
**Inputs → Outputs:** `splash.svg.gz` → a bitmap exported by hand; its
Inkscape export target is `splash.png` and its 120 × 96 page has the same
5:4 shape as `trelby/resources/logo.jpg` (375 × 300 px), the image the
program shows.

## Files
- `splash.svg.gz` — gzipped Inkscape SVG of the splash / About picture
  (by its size and export name; no script links the two).

## Key facts / gotchas
- Not read by the program or any script; `trelby/resources/logo.jpg` is
  what the splash shows (`trelby/splash.py:39`). The version and URL on the
  splash are drawn by code over the image (`trelby/splash.py:84-86`), not
  part of the artwork.

## Touchpoints
- Matches: `trelby/resources/logo.jpg`.
