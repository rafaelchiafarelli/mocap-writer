# spellcheck — mocap-writer

**Status:** Planned (2026-10-27). A feature, not a bug (Rafael,
2026-10-27): Rafael writes in Brazilian Portuguese and the spell checker
only knows English.

**Goal:** Tools → Spell checker checks a script in Brazilian Portuguese
(pt-BR), with useful suggestions, and English stays available.

**Scope:** a pt-BR dictionary in the Docker image, a setting for the
dictionary language, the checker and its suggestions working with it.

**Out of scope:** checking while typing (underlining misspelled words);
other languages; translating the program's menus (English only, Rafael
2026-10-27); a per-script language (waits for fountain-native/settings/1,
the script settings record).

**Initiative gate:** Rafael runs the spell checker on one of his pt-BR
scripts and the words it stops on are real mistakes or names, and its
suggestions are useful.

Epics: `epics/README.md`.
