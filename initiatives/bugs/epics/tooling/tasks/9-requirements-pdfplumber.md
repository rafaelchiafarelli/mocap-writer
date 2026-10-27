## 9. requirements.txt lacks pdfplumber

- **Status:** Open
- **Symptom:** `requirements.txt` lists `wxPython`, `lxml`, `reportlab`, `pytest` but not `pdfplumber`, which `setup.cfg:22` and `docker/requirements.in:9` have; `tests/test_pdfimport.py` reaches `import pdfplumber` (`trelby/pdfimport.py:282`).
- **Where:** `requirements.txt`
- **Reproduce:** Found by reading the code while writing the root `CLAUDE.md` (2026-10-26).
- **Impact:** the GitHub workflow, which installs from `requirements.txt`, would fail the PDF import tests; it runs only on pushes to `main`.
- **Likely fix:** add `pdfplumber` to `requirements.txt`.
