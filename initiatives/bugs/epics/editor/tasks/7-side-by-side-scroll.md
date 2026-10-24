## 7. Side-by-side ignores the scroll direction

- **Status:** Open
- **Symptom:** `makeLineVisible` in side-by-side mode always jumps the line to the top.
- **Where:** `ViewModeSideBySide.makeLineVisible` (`trelby/viewmode.py:539-540`)
- **Reproduce:** side-by-side mode, move the cursor past the bottom of the window.
- **Impact:** jumpy scrolling in that mode.
