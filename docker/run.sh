#!/usr/bin/env bash
# Launch mocap-writer (Trelby) from its Docker image, with the window shown on
# the host's display. Nothing is installed on the host besides Docker.
#
#   docker/run.sh [work-dir]
#
# work-dir (default: current directory) is mounted at its own path, and the
# file dialogs start there. The Windows drives (/mnt/c, /mnt/g, ...) are
# mounted at their own paths too, so every dialog shows the same paths as
# WSL and any folder visible from Windows can be opened. Settings persist in ~/.config/mocap-writer on the host.
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

# the Windows drives WSL mounts as /mnt/<letter>, each at the same path
drive_args=()
for d in /mnt/[a-z]; do
    [ -d "$d" ] && drive_args+=(-v "$d":"$d")
done

exec docker run --rm \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    "${display_args[@]}" \
    -v "$repo":/app:ro \
    "${drive_args[@]}" \
    -v "$work":"$work" -w "$work" -e MOCAP_WRITER_WORK_DIR="$work" \
    -v "$config":/config \
    "$image"
