# mocap-writer image: the environment Trelby runs in (DEPENDENCIES.md rule B).
# Shared Mocap Studio base: Ubuntu 24.04, system Python 3.12, pinned by digest;
# Python deps only from the hashed lockfile. The source is not copied in:
# docker/run.sh mounts the repository, so code edits need no rebuild.
FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
# GTK3 and the libraries the prebuilt wxPython wheel links against; fonts for the editor;
# evince (GPL-2.0+) shows Print and report PDFs, docbook-xsl (permissive DocBook XSL
# licence) turns doc/manual.xml into the Help → Manual page.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 python3-venv \
        libgtk-3-0t64 libnotify4 libsm6 libxtst6 libsdl2-2.0-0 libcurl4t64 libpcre2-32-0 \
        libgl1 libglu1-mesa libegl1 \
        fonts-dejavu-core fonts-liberation \
        evince docbook-xsl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /build-py
COPY requirements.lock ./
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --require-hashes \
        --find-links https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-24.04/ \
        --only-binary wxpython -r requirements.lock
# Trelby keeps its settings under $XDG_CONFIG_HOME/trelby; run.sh mounts /config.
# GTK settings in memory: the container has no D-Bus session for dconf.
ENV XDG_CONFIG_HOME=/config GSETTINGS_BACKEND=memory NO_AT_BRIDGE=1
# mocap-contracts from its submodule in the mounted repository (pinned to a tag there;
# a hashed lock can't hold a git+ URL); its generated packages ship top-level in gen/python.
ENV PYTHONPATH=/app/third_party/mocap-contracts:/app/third_party/mocap-contracts/gen/python
USER ubuntu
WORKDIR /work
CMD ["/opt/venv/bin/python", "/app/trelby.py"]
