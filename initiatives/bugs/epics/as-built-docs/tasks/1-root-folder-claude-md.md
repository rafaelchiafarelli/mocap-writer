## 1. The repository root has no CLAUDE.md

- **Status:** Open
- **Symptom:** No `CLAUDE.md` for the root; `.travis.yml`, `README.dev`, `README.md`, `TODO`, `icon32.ico`, `long_description.txt` and `t.bat` (`short.trelby` was deleted 2026-10-25) have no bullet anywhere, and `trelby.py`, `Makefile`, `pyproject.toml`, `setup.cfg`, `requirements.txt`, `t_0*.sh`, `LICENSE`, `.gitignore` are only mentioned in passing.
- **Where:** root of the repository; the as-built task 3 listed 14 folders and left the root out
- **Reproduce:** as-built review, 2026-10-24.
- **Impact:** a session working at the root gets no context.
- **Likely fix:** add `CLAUDE.md` at the root.
