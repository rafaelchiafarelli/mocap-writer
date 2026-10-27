## 8. Folders above the work dir cannot be written under `docker/run.sh`

- **Status:** Fixed (2026-10-25) — fixes/00006d/run-home-mount
- **Symptom:** In the editor's file dialogs, `/home/rafael/workspace` (and
  every folder above the work dir) was visible but "Create folder" failed
  with no permission; saving in the work dir worked.
- **Where:** `docker/run.sh` mounted only the work dir at its own path, so
  Docker created the folders above it inside the container as empty,
  root-owned mount points: they show only the path down to the work dir,
  the container user cannot write them, and nothing written there would
  reach the host.
- **Reproduce:** `docker/run.sh` from `mocap-writer`, Save As, go up to
  `/home/rafael/workspace`, create a folder (Rafael, 2026-10-25); in the
  image, `ls -ld /home/rafael/workspace` showed `root root` with only
  `mocap-studio` inside.
- **Impact:** high: scripts could not be saved in a new folder outside the
  work dir (e.g. a film root under the workspace).
- **Fix:** `run.sh` also mounts the host `$HOME` at its own path
  (`docker/run.sh:54-57`); checked by creating a folder in
  `/home/rafael/workspace` from the container, owned by the host user on
  the host.
