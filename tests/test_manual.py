import os

import pytest

import tests.u as u  # first: trelby.util cannot be the first trelby module loaded
import trelby.manual as manual

# Help -> Manual: the page is made from doc/manual.xml when no prebuilt
# trelby/manual.html exists (bugs/editor/11)

DOC = os.path.join(os.path.dirname(__file__), "..", "doc")


@pytest.mark.skipif(
    not os.path.isdir(manual.DEB_XSL_DIR), reason="needs the docbook-xsl package"
)
def testBuildFromDocBook(tmp_path):
    html = manual.build(str(tmp_path / "none.html"), DOC)

    assert "<title>Trelby Manual</title>" in html
    assert "2.4.16.2" in html


def testPrebuiltWins(tmp_path):
    pre = tmp_path / "manual.html"
    pre.write_text("<html>prebuilt</html>", encoding="utf-8")

    assert manual.build(str(pre), DOC) == "<html>prebuilt</html>"


def testMissingSourceIsManualError(tmp_path):
    with pytest.raises(manual.ManualError):
        manual.build(str(tmp_path / "none.html"), str(tmp_path))
