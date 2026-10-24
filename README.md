# mocap-writer

**This is a fork of [Trelby](https://github.com/trelby/trelby)** (GPL-2.0),
the open-source screenplay writer in Python, adapted as the script editor of
Mocap Studio.

**Why a fork of Trelby.** Mocap Studio turns a film's script into a shot
list, 3D blocking and storyboards, and the script is the source of truth for
all of that. We want it written in a real screenwriting tool whose output is
**Fountain**, a plain-text format our own parser reads and git can diff.
Trelby is the open-source editor that fits the project: it is Python (the
project's language), runs on Windows and Linux, and its GPL-2.0 license
allows commercial use. Proprietary tools such as Celtx were rejected because
they keep the script in a closed format on their servers.

What changes here is driven by the Mocap Studio workflow (planning lives in
`initiatives/`, process in `.claude/skills/mocap-workflow/`). Upstream
updates are pulled with `git fetch upstream && git merge upstream/master`
(`upstream` = `https://github.com/trelby/trelby.git`). This fork stays under
GPL-2.0; Trelby's original README follows.

**Running it.** Only Docker is needed on the host (Windows 11 with WSL2, or a
Linux desktop); nothing else gets installed:

```bash
docker/run.sh [work-dir]   # builds the image on first use, then opens the window
```

`work-dir` (default: the current directory) is where scripts are opened and
saved; settings persist in `~/.config/mocap-writer`. The image
(`docker/Dockerfile`, hashed `docker/requirements.lock`) holds only the
environment: the repository is mounted, so code edits need no rebuild.

---

## Trelby (upstream README)
## Screenplay writing software
Trelby is a screenplay writing program. See https://www.trelby.org/ for
more details.

### About this project
This project has recently been updated by merging the fork: https://github.com/limburgher/trelby.

Updates include:
- a conversion to Python 3
- enhancements
- updating the Windows packaging to provide a Windows build (still in progress)

### Installation

#### Fedora

sudo dnf install trelby

#### Windows (Chocolatey)

Once chocolatey is set up (https://chocolatey.org/install):

`choco install trelby`

#### Flatpak

`flatpak install trelby`

#### From PyPi

`pip (or pip3) install trelby`

#### From source

1. git clone https://github.com/trelby/trelby.git

2. cd trelby

3. pip3 install -r requirements.txt  
   *Depending on your python version, you might run into https://github.com/wxWidgets/Phoenix/issues/2296. We recommend executing `pip3 install attrdict3` before installing the requirements in that case. If that still doesn't work, we recommend upgrading your python version.*

4. make

5. ./trelby.py