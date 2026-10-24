## 1. Scene ids and automatic numbering

- **Type:** code
- **Depends on:** io/1; **Rafael's decision on numbering** (open, 2026-10-23)
- **Contract (proposal, to confirm):**
  - In: a scene heading
  - Requires: every scene gets a hidden id when it is created, written in the
    heading as a note (`INT. SALA - NOITE [[id:a3f9]]`) and hidden in the
    editor; the visible number is automatic (position in the script) and
    renumbers on insert/delete/move; everything outside the script points to
    the id, never the number; a pasted scene with a duplicate id gets a new
    one; a **lock** command (Rafael's, never automatic) freezes the numbers,
    after which new scenes get letters (`13A`)
  - Delivers: ids, numbering, lock, and the id rule for other repositories
- **Pre-work:** Rafael's decision, recorded in this file
- **Out of scope:** INT/EXT prefixes (later)
- **Tests:** insert/delete/move renumber; ids never change; duplicate id on
  paste; lock then insert gives `13A`; ids survive the Fountain round trip
