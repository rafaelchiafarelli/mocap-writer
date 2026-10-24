import glob
import os
import re

import wx

# wx.<name> references that are not attributes: submodules imported
# elsewhere (wx.html, wx.svg), a "wx.GTK" in a comment, and the "wx.WXK_"
# prefix in util.py's key tables
NOT_ATTRIBUTES = {"html", "svg", "GTK", "WXK_"}

# known bugs, still open
KNOWN = {
    # initiatives/bugs/epics/editor/tasks/18-commands-save-overwrite-prompt.md
    ("commandsdlg.py", "OVERWRITE_PROMPT"),
}


# every wx.<name> used in trelby/ exists in the installed wxPython: names
# removed in wxPython 4 only fail when their dialog opens (bugs/editor/17)
def testWxNamesExist():
    root = os.path.join(os.path.dirname(__file__), "..", "trelby")
    missing = []
    for path in sorted(glob.glob(os.path.join(root, "**", "*.py"), recursive=True)):
        with open(path, encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                for name in re.findall(r"\bwx\.([A-Za-z_][A-Za-z0-9_]*)", line):
                    key = (os.path.basename(path), name)
                    if name in NOT_ATTRIBUTES or key in KNOWN or hasattr(wx, name):
                        continue
                    missing.append("%s:%d wx.%s" % (os.path.relpath(path, root), i, name))

    assert missing == []
