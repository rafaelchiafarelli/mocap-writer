import tests.u as u
import trelby.config as config
import trelby.screenplay as scr
import trelby.translations as translations

_ = translations.trelby_translations_load()

# the Tab / Shift+Tab cycle (editor-ux/typing/1): one list in ConfigGlobal,
# saved with the global config, instead of a pair of fields per element.


def newCfgGl():
    u.init()

    return config.ConfigGlobal()


def testDefaultCycle():
    cfgGl = newCfgGl()

    assert cfgGl.tabOrder == [scr.SCENE, scr.ACTION, scr.CHARACTER, scr.DIALOGUE]
    assert cfgGl.nextTypeTab(scr.DIALOGUE) == scr.SCENE
    assert cfgGl.prevTypeTab(scr.SCENE) == scr.DIALOGUE


def testOutsideCycle():
    cfgGl = newCfgGl()

    for lt in (scr.PAREN, scr.TRANSITION, scr.SHOT, scr.ACTBREAK, scr.NOTE):
        assert cfgGl.nextTypeTab(lt) == scr.ACTION
        assert cfgGl.prevTypeTab(lt) == scr.ACTION

    cfgGl.tabOrder = [scr.SCENE, scr.CHARACTER]
    assert cfgGl.nextTypeTab(scr.NOTE) == scr.SCENE


def testSaveLoad():
    cfgGl = newCfgGl()
    cfgGl.tabOrder = [scr.ACTION, scr.SHOT, scr.SCENE]

    cfgGl2 = newCfgGl()
    cfgGl2.load(cfgGl.save())

    assert cfgGl2.tabOrder == [scr.ACTION, scr.SHOT, scr.SCENE]
    assert cfgGl2.nextTypeTab(scr.SCENE) == scr.ACTION


def testRecalc():
    cfgGl = newCfgGl()

    cfgGl.tabOrder = [scr.SCENE, scr.ACTION, scr.SCENE, scr.NOTE]
    cfgGl.recalc()
    assert cfgGl.tabOrder == [scr.SCENE, scr.ACTION, scr.NOTE]

    cfgGl.tabOrder = [scr.SCENE]
    cfgGl.recalc()
    assert cfgGl.tabOrder == config.TAB_ORDER_DEFAULT
    assert cfgGl.tabOrder is not config.TAB_ORDER_DEFAULT
