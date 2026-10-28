## 12. No horizontal scrolling

- **Status:** Open
- **Symptom:** When the page is wider than the window (a high zoom or a narrow window), the page is left-aligned and its right part, cursor included, is not shown.
- **Where:** `cox` clamped at 0 in draft and layout (`trelby/viewmode.py:217`, `trelby/viewmode.py:301`); the editor has only a vertical scroll bar (`trelby/trelbypanel.py:7`)
- **Reproduce:** zoom to 300 % in a window narrower than about 2400 px.
- **Impact:** text past the right edge can't be seen; 200 % fits a full-HD screen (Rafael, 2026-10-24: leave it until it gets in the way).
- **Likely fix:** a horizontal offset that follows the cursor, or a horizontal scroll bar.
