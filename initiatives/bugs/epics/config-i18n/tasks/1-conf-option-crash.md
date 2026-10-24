## 1. `--conf` crashes at startup

- **Status:** Open
- **Symptom:** `trelby.py --conf <file>` raises `TypeError`.
- **Where:** `str(sys.argv[i + 1], "UTF-8", "ignore")` on a `str` (`trelby/opts.py:28`)
- **Reproduce:** `trelby.py --conf x.conf`.
- **Impact:** the option cannot be used.
- **Likely fix:** `conf = sys.argv[i + 1]`.
