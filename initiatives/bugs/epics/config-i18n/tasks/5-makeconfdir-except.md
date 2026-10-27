## 5. Invalid except clause in makeConfDir

- **Status:** Fixed (2026-10-26) — fixes/000086/one-line-crashes
- **Symptom:** `except OSError(os.errno, os.strerror)` would raise instead of catching.
- **Where:** `trelby/globaldata.py:93`; only reached if `misc.init` failed to create `confPath` (`trelby/misc.py:72-73`)
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** latent.
- **Likely fix:** `except OSError`.
