## 11. Help → Manual opens a missing file

- **Status:** Open
- **Symptom:** Help → Manual opens `trelby/manual.html`, which a checkout and the Docker image do not have.
- **Where:** `trelby/trelbyframe.py:969`; the file is a build product of `Makefile` and needs DocBook, not in the image
- **Reproduce:** Help → Manual.
- **Impact:** no manual in the editor.
