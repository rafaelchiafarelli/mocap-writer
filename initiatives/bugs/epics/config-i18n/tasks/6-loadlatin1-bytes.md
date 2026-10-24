## 6. loadLatin1EncodedFile reads bytes; loadFile can return unbound

- **Status:** Open
- **Symptom:** `loadLatin1EncodedFile` passes `"ISO-8859-1"` as the `binary` flag, so it returns bytes; on `MemoryError` `loadFile` returns an unbound `ret`.
- **Where:** `trelby/util.py:1026`, `trelby/util.py:1003-1020`
- **Reproduce:** Found by reading the code in the as-built review (2026-10-24).
- **Impact:** latent for callers of these helpers.
