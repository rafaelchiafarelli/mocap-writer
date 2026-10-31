#!/usr/bin/env bash
# Launch mocap-writer (Trelby) from its Docker image, with the window shown on
# the host's display. Nothing is installed on the host besides Docker.
#
#   docker/run.sh [work-dir]
#
# work-dir (default: current directory) is mounted at its own path, and the
# file dialogs start there. The Windows drives (/mnt/c, /mnt/g, ...) are
# mounted at their own paths too, so every dialog shows the same paths as
# WSL and any folder visible from Windows can be opened; so is the host home
# ($HOME), so every folder under it can be browsed and written. Settings
# persist in ~/.config/mocap-writer on the host.
# Display: WSLg on Windows 11 (/mnt/wslg), or X11 on a Linux desktop.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(cd "${1:-.}" && pwd)"
image="mocap-writer:dev"
config="$HOME/.config/mocap-writer"
mkdir -p "$config"

# build on every start, as test.sh does: cached, so it only takes time after
# docker/ changed, and an old image never runs without its new packages
docker build -q -t "$image" -f "$repo/docker/Dockerfile" "$repo/docker" >/dev/null

display_args=(-e DISPLAY="${DISPLAY:-:0}" -v /tmp/.X11-unix:/tmp/.X11-unix)
if [ -d /mnt/wslg ]; then
    display_args+=(-v /mnt/wslg:/mnt/wslg
                   -e WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
                   -e XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
                   -e PULSE_SERVER=/mnt/wslg/PulseServer)
fi

# Menus, toolbar and dialogs follow GTK's dark variant when the Dark theme is
# chosen in Settings → Colors (Theme:1 in Trelby's config; read at start).
theme_args=()
if grep -qx 'Theme:1' "$config/trelby/default.conf" 2>/dev/null; then
    theme_args=(-e GTK_THEME=Adwaita:dark)
fi

# Instrumented PDF import: MOCAP_WRITER_PDF_TRACE=<dir> (its WSL path; the
# drives and the work dir are mounted at their own paths) writes a .trace.tsv per imported PDF there.
trace_args=()
if [ -n "${MOCAP_WRITER_PDF_TRACE:-}" ]; then
    trace_args=(-e MOCAP_WRITER_PDF_TRACE="$MOCAP_WRITER_PDF_TRACE")
fi

# the Windows drives WSL mounts as /mnt/<letter>, each at the same path
drive_args=()
for d in /mnt/[a-z]; do
    [ -d "$d" ] && drive_args+=(-v "$d":"$d")
done

# the host home at its own path too: otherwise the folders above the work dir
# are empty root-owned stand-ins Docker makes for the mount, which show in
# the dialogs but cannot be written (bugs/tooling/8)
home_args=(-v "$HOME":"$HOME")

exec docker run --rm \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    "${display_args[@]}" \
    "${theme_args[@]}" \
    "${trace_args[@]}" \
    -v "$repo":/app:ro \
    "${drive_args[@]}" \
    "${home_args[@]}" \
    -v "$work":"$work" -w "$work" -e MOCAP_WRITER_WORK_DIR="$work" \
    -v "$config":/config \
    "$image"
