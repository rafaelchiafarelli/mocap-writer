#!/bin/bash
# spellcheck/study/1: reproduce every measurement in a throwaway container
# started from the writer's image. Run from the repository root, after
# docker/test.sh (or run.sh) has built mocap-writer:dev. Nothing is kept:
# the container is removed at the end; the image is not changed.
set -e
M=/app/initiatives/spellcheck/epics/study/tasks/1-dictionary-study/measure.py
C=spellstudy-$$
docker run -d --name "$C" --user root -v "$PWD":/app:ro mocap-writer:dev sleep infinity >/dev/null
trap 'docker rm -f "$C" >/dev/null' EXIT
x() { docker exec -w /app "$C" bash -c "$1"; }

x 'apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
     hunspell-pt-br hunspell-tools libhunspell-1.7-0 libenchant-2-2 python3-hunspell time >/dev/null'
x 'dpkg-query -W -f="\${Package} \${Version} \${Installed-Size}KB\n" hunspell-pt-br libhunspell-1.7-0 libenchant-2-2'
x 'grep -A2 "^Files: dictionaries/pt_BR/" /usr/share/doc/hunspell-pt-br/copyright; sed -n 5,14p /usr/share/hunspell/pt_BR.aff'

echo "== option 1: unmunch to a flat list"
x 'cd /tmp && /usr/bin/time -f "unmunch: %e s, %M KB" unmunch /usr/share/hunspell/pt_BR.dic /usr/share/hunspell/pt_BR.aff 2>/dev/null >unm.txt; wc -l <unm.txt'
# Trelby splits words at "-" (util.isWordBoundary), so hyphenated forms can never be looked up
x 'cd /tmp && grep -v -- - unm.txt | python3 -c "import sys; s={l.rstrip(\"\n\").lower() for l in sys.stdin}-{\"\"}; open(\"flat.txt\",\"w\").write(\"\n\".join(sorted(s))+\"\n\")" \
     && wc -l <flat.txt && gzip -9 -k flat.txt && ls -l flat.txt flat.txt.gz'
# the same without the PFX (prefix) rules
x 'cd /tmp && grep -v ^PFX /usr/share/hunspell/pt_BR.aff >nopfx.aff && unmunch /usr/share/hunspell/pt_BR.dic nopfx.aff 2>/dev/null | grep -v -- - \
     | python3 -c "import sys; s={l.rstrip(\"\n\").lower() for l in sys.stdin}-{\"\"}; open(\"flat_nopfx.txt\",\"w\").write(\"\n\".join(sorted(s))+\"\n\")" \
     && wc -l <flat_nopfx.txt && gzip -9 -k flat_nopfx.txt && ls -l flat_nopfx.txt flat_nopfx.txt.gz'
for f in /app/trelby/dict_en.dat /tmp/flat_nopfx.txt /tmp/flat.txt; do
    echo "== flat $f"; x "/opt/venv/bin/python $M flat $f"
done

echo "== option 2: Hunspell engines"
x "python3 $M hunspell"
x 'python3 -m venv /tmp/sv && /tmp/sv/bin/pip install -q pyenchant==3.3.0 spylls==0.1.7'
x "/tmp/sv/bin/python $M enchant"
x "/tmp/sv/bin/python $M spylls"
