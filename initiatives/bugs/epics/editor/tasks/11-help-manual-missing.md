## 11. Help → Manual opens a missing file

- **Status:** Fixed (2026-10-27) — fixes/000093/viewers: the manual is made from doc/ in the image (docbook-xsl) and shown in the editor (Rafael chose to build it in the image)
- **Symptom:** Help → Manual opens `trelby/manual.html`, which a checkout and the Docker image do not have.
- **Where:** `trelby/trelbyframe.py:980`; the file is a build product of `Makefile` and needs DocBook, not in the image
- **Reproduce:** Help → Manual.
- **Impact:** no manual in the editor.
