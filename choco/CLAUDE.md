# choco — upstream Chocolatey (Windows) package

**Role:** A Chocolatey package that installs Trelby from PyPI with `pip3`
and adds a Start-menu shortcut. Upstream Trelby's; not used by Mocap Studio.
**Entry points:** `choco pack` on `trelby.nuspec`.
**Inputs → Outputs:** nuspec + install scripts → `trelby.<version>.nupkg`.

## Files
- `trelby.nuspec` — package metadata, version `2.4.16.2`, depends on the
  `python3` package.
- `tools/chocolateyinstall.ps1` — `pip3 install trelby==2.4.16.2`, then a
  shortcut to `C:\Python313\Scripts\trelby.exe` with
  `trelby\resources\icon256.ico` (`choco/tools/chocolateyinstall.ps1:1-2`).
- `tools/chocolateyuninstall.ps1` — `pip3 uninstall`, delete the shortcut.
- `tools/LICENSE.txt` — GPL text shipped in the package.

## Key facts / gotchas
- The shortcut paths hard-code Python 3.13 in `C:\Python313`.
- The version is repeated here, in `setup.cfg`, `trelby/misc.py:20` and
  `doc/version.xml`.

## Touchpoints
- Uses: the PyPI `trelby` package (built from `setup.cfg`).
