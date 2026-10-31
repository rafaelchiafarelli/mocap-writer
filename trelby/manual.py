# Help -> Manual: the user manual as one HTML page, shown in a window of
# the program (the Docker image has no browser). A trelby/manual.html is
# used if one exists (nothing builds it any more); otherwise the page is
# made from doc/manual.xml with the DocBook XSL stylesheets (the docbook-xsl
# package) through lxml.

import os
import webbrowser

import wx
import wx.html
from lxml import etree

import trelby.misc as misc

# where Debian / Ubuntu put the stylesheets doc/html-stylesheet-deb.xsl
# imports; other systems: doc/html-stylesheet.xsl's path
DEB_XSL_DIR = "/usr/share/sgml/docbook/stylesheet/xsl/"


class ManualError(Exception):
    pass


# the manual as an HTML string, from the prebuilt file if there is one,
# else from the DocBook source in docDir. raises ManualError.
def build(prebuilt, docDir):
    if os.path.isfile(prebuilt):
        with open(prebuilt, encoding="utf-8") as f:
            return f.read()

    if os.path.isdir(DEB_XSL_DIR):
        xslName = "html-stylesheet-deb.xsl"
    else:
        xslName = "html-stylesheet.xsl"

    try:
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True, no_network=True)
        doc = etree.parse(os.path.join(docDir, "manual.xml"), parser)
        xsl = etree.XSLT(etree.parse(os.path.join(docDir, xslName)))
        html = str(xsl(doc))
    except (OSError, etree.Error) as e:
        raise ManualError(
            _(
                "The manual could not be made from {}: {}\n\nIt needs the "
                "DocBook XSL stylesheets (the docbook-xsl package)."
            ).format(docDir, e)
        )

    return html


# a window showing the manual; links inside it jump to their anchor, other
# links go to the system browser (if there is one)
class ManualFrame(wx.Frame):
    def __init__(self, parent, html):
        wx.Frame.__init__(self, parent, -1, _("Trelby Manual"), size=(800, 700))

        self.html = ManualHtml(self)
        self.html.SetPage(html)


class ManualHtml(wx.html.HtmlWindow):
    def OnLinkClicked(self, link):
        href = link.GetHref()

        if href.startswith("#"):
            self.ScrollToAnchor(href[1:])
        else:
            webbrowser.open(href)


# Help -> Manual
def show(parent):
    try:
        html = build(
            misc.getFullPath("trelby/manual.html"), misc.getFullPath("doc")
        )
    except ManualError as e:
        wx.MessageBox(str(e), _("Error"), wx.OK, parent)

        return

    ManualFrame(parent, html).Show()
