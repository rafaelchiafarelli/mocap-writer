## 3. Subfolders without their own CLAUDE.md

- **Status:** Open
- **Symptom:** `choco/tools/`, `debian/source/`, `tests/fixtures/custom-font/`, `trelby/locales/en/LC_MESSAGES/` and `trelby/locales/it/LC_MESSAGES/` have no `CLAUDE.md`; their files are bulleted in the parent's.
- **Where:** those folders
- **Reproduce:** as-built review, 2026-10-24.
- **Impact:** none in practice; the rule says one per folder.
- **Likely fix:** Rafael to decide: accept parent coverage as the rule for leaf folders, or add the files.
