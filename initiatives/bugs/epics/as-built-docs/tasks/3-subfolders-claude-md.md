## 3. Subfolders without their own CLAUDE.md

- **Status:** Fixed (2026-10-26) — fixes/000082/as-built-docs
- **Symptom:** `choco/tools/`, `debian/source/`, `tests/fixtures/custom-font/`, `trelby/locales/en/LC_MESSAGES/` and `trelby/locales/it/LC_MESSAGES/` have no `CLAUDE.md`; their files are bulleted in the parent's.
- **Where:** those folders
- **Reproduce:** as-built review, 2026-10-24.
- **Impact:** none in practice; the rule says one per folder.
- **Likely fix:** Rafael to decide: accept parent coverage as the rule for leaf folders, or add the files.
- **Resolution:** Rafael chose parent coverage (2026-10-26): a folder with no code, only data files or subfolders, needs no `CLAUDE.md` of its own when its parent's lists each of its files (`mocap-workflow`, "As-built documentation"). The parents already list them; the root's `CLAUDE.md` (bug 1) lists `.github/`.
