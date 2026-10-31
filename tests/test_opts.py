import sys

import trelby.opts as opts

# the command line: --test, --conf <file>, and scripts to open


def testConfAndScripts(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["trelby.py", "--conf", "my.conf", "a.fountain", "b.fountain"]
    )
    opts.init()

    # --conf used to raise TypeError (bugs/config-i18n/1)
    assert opts.conf == "my.conf"
    assert opts.filenames == ["a.fountain", "b.fountain"]
    assert not opts.isTest
