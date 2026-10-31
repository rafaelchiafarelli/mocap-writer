## 2. Sync to spec command

- **Status:** Done (2026-10-31) — Script → Sync to spec… (F5, toolbar `sync.svg`), `trelby/syncdlg.py`; checked through the real window.
- **Type:** code (UI)
- **Depends on:** sync/1
- **Contract:**
  - In: the open script and its film root
  - Requires: a **Sync to spec** menu item, toolbar button and shortcut run
    `sync_run()` on the saved script (unsaved changes → ask to save first);
    a panel lists the changes grouped by scene, each line jumps to the scene;
    **Accept** calls `sync_accept()`; nothing in the bible changes from this
    command
  - Delivers: the command and the change panel
- **Pre-work:** —
- **Out of scope:** running on every save (a later task, after Rafael has
  used the button); affected records (sync/3 adds them to this panel)
- **Tests:** command with no film root → clear message; unsaved script →
  save prompt; panel lines match the change set
