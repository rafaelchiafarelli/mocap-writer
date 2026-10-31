## 10. The image cannot load SVG theme assets

- **Status:** Fixed (2026-10-31) — fixes/0000a8/svg-pixbuf-loader
- **Symptom:** the terminal shows `Gtk-WARNING … Could not load a pixbuf
  from /org/gtk/libgtk/theme/Adwaita/assets/check-symbolic.svg`; check
  marks GTK draws from that asset (check boxes, check menu items) can be
  missing.
- **Where:** the image installs GTK3 but no SVG loader for gdk-pixbuf
  (`docker/Dockerfile:10-17`; the loaders folder has no `libpixbufloader-svg`).
- **Reproduce:** `docker/run.sh`, then open a checklist (From script…) or
  the View menu (Rafael, 2026-10-31).
- **Impact:** a checked box may look unchecked.
- **Likely fix:** install `librsvg2-common` (LGPL-2.1+) in the image.
