# workflows — upstream GitHub Actions CI

**Role:** Runs the test suite on GitHub for Python 3.9–3.13.
**Entry points:** `main.yml`, on push to `main` and on pull requests
(`.github/workflows/main.yml:1-6`).
**Inputs → Outputs:** repository → test results on GitHub.

## Files
- `main.yml` — Ubuntu runner; apt `libgtk-3-dev`, `libsdl2-2.0`,
  `libwxgtk3.2-dev`; pip install from the unpinned `requirements.txt` with
  wxPython from the extras wheel index; caches the Python install keyed on
  `requirements.txt`; then `pytest` (`.github/workflows/main.yml:11-53`).

## Key facts / gotchas
- Inherited from upstream. It does not use `docker/` or
  `docker/requirements.lock`, so CI and the Mocap Studio environment can
  test different package versions; Mocap Studio work is verified with
  `docker/test.sh`.
- It triggers on `main`, not `dev`, and there is no PR workflow in this
  project, so it runs only when something is pushed to `main` on GitHub.

## Touchpoints
- Runs: `tests/`.
- Depends on: `requirements.txt`.
