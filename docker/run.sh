#!/usr/bin/env bash
# Launch mocap-writer (Trelby) from its Docker image, with the window shown on
# the host's display. Nothing is installed on the host besides Docker.
#
#   docker/run.sh [work-dir]
#
# work-dir (default: current directory) is mounted at /work: open and save
# scripts there. Settings persist in ~/.config/mocap-writer on the host.
# Display: WSLg on Windows 11 (/mnt/wslg), or X11 on a Linux desktop.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(cd "${1:-.}" && pwd)"
image="mocap-writer:dev"
config="$HOME/.config/mocap-writer"
mkdir -p "$config"

if ! docker image inspect "$image" >/dev/null 2>&1; then
    docker build -t "$image" -f "$repo/docker/Dockerfile" "$repo/docker"
fi

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

exec docker run --rm \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    "${display_args[@]}" \
    "${theme_args[@]}" \
    -v "$repo":/app:ro \
    -v "$work":/work \
    -v "$config":/config \
    "$image"
