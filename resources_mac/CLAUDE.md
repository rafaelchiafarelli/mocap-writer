# resources_mac — macOS application icon

**Role:** The `.icns` icon for a macOS app bundle.
**Entry points:** none in this repository; no build script here makes a
macOS bundle.
**Inputs → Outputs:** —

## Files
- `icon.icns` — application icon, meant to be generated from
  `trelby/resources/icon*.png` by `tools/update_icns.py`.

## Key facts / gotchas
- Nothing in the code, packaging or Docker setup reads this file.
- `tools/update_icns.py` rebuilds it from `trelby/resources/icon*.png`
  (needs `icnsutil`, `tools/CLAUDE.md`).

## Touchpoints
- Written by: `tools/update_icns.py`.
