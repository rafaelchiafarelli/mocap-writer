import tests.u as u
import trelby.config as config
import trelby.pml as pml
import trelby.translations as translations

_ = translations.trelby_translations_load()

# the screen zoom (editor-ux/view/1): a ConfigGlobal setting that scales the
# screen fonts and the draft row height, never the PDF.


def newCfgGl():
    u.init()

    return config.ConfigGlobal()


def testDefault():
    cfgGl = newCfgGl()

    assert cfgGl.zoom == 100
    assert cfgGl.zoomScale(12) == 12


def testStepsAndLimits():
    cfgGl = newCfgGl()

    assert cfgGl.zoomIn()
    assert cfgGl.zoom == 110

    assert cfgGl.zoomOut() and cfgGl.zoomOut()
    assert cfgGl.zoom == 90

    assert cfgGl.zoomReset()
    assert cfgGl.zoom == 100
    assert not cfgGl.zoomReset()

    cfgGl.setZoom(config.ZOOM_MAX)
    assert not cfgGl.zoomIn()
    assert cfgGl.zoom == 300

    cfgGl.setZoom(config.ZOOM_MIN)
    assert not cfgGl.zoomOut()
    assert cfgGl.zoom == 50


def testSetZoomSnapsAndClamps():
    cfgGl = newCfgGl()

    cfgGl.setZoom(123)
    assert cfgGl.zoom == 120

    cfgGl.setZoom(1000)
    assert cfgGl.zoom == 300

    cfgGl.setZoom(0)
    assert cfgGl.zoom == 50


def testScalesScreenSizes():
    cfgGl = newCfgGl()
    cfgGl.setZoom(150)

    # what ConfigGui applies to the screen fonts and fontYdelta
    assert cfgGl.zoomScale(12) == 18
    assert cfgGl.zoomScale(cfgGl.fontYdelta) == 27

    # the unzoomed values stay in the config
    assert cfgGl.fontYdelta == 18


def testSurvivesRestart():
    cfgGl = newCfgGl()
    cfgGl.setZoom(170)

    cfgGl2 = newCfgGl()
    cfgGl2.load(cfgGl.save())

    assert cfgGl2.zoom == 170


def testLoadClampsHandEditedValue():
    cfgGl = newCfgGl()
    cfgGl.load("Zoom:900\n")

    assert cfgGl.zoom == 300


def textOps(sp):
    doc = sp.generatePML(True)

    return [
        (op.text, op.x, op.y, op.size)
        for page in doc.pages
        for op in page.ops
        if isinstance(op, pml.TextOp)
    ]


def testPdfNotAffected():
    sp = u.load()
    before = textOps(sp)
    fontSize = sp.cfg.fontSize

    sp.cfgGl.setZoom(250)

    assert sp.cfg.fontSize == fontSize
    assert textOps(sp) == before
