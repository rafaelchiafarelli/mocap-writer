import tests.u as u
import trelby.config as config
import trelby.translations as translations
import trelby.util as util

_ = translations.trelby_translations_load()

# the color themes (editor-ux/view/2): Light and Dark, each a full set of
# the ConfigGlobal colors, switchable without losing custom colors.


def newCfgGl():
    u.init()

    return config.ConfigGlobal()


def rgb(c):
    return (c.r, c.g, c.b)


def testDefaultIsLight():
    cfgGl = newCfgGl()

    assert cfgGl.theme == config.THEME_LIGHT
    assert rgb(cfgGl.textBgColor) == (255, 255, 255)


def testDarkSetDefinesEveryColor():
    cfgGl = newCfgGl()

    assert set(config.DARK_COLORS) == set(cfgGl.cvars.color)

    for r, g, b in config.DARK_COLORS.values():
        assert all(0 <= v <= 255 for v in (r, g, b))


def testSetThemeAppliesItsColors():
    cfgGl = newCfgGl()

    assert cfgGl.setTheme(config.THEME_DARK)
    assert not cfgGl.setTheme(config.THEME_DARK)

    for name, val in config.DARK_COLORS.items():
        assert rgb(getattr(cfgGl, name)) == val

    assert cfgGl.setTheme(config.THEME_LIGHT)
    assert rgb(cfgGl.textBgColor) == (255, 255, 255)


def testSwitchingKeepsCustomColors():
    cfgGl = newCfgGl()

    cfgGl.textColor = util.MyColor(10, 20, 30)
    cfgGl.setTheme(config.THEME_DARK)
    cfgGl.textColor = util.MyColor(200, 210, 220)

    cfgGl.setTheme(config.THEME_LIGHT)
    assert rgb(cfgGl.textColor) == (10, 20, 30)

    cfgGl.setTheme(config.THEME_DARK)
    assert rgb(cfgGl.textColor) == (200, 210, 220)


def testThemesSurviveRestart():
    cfgGl = newCfgGl()

    cfgGl.noteColor = util.MyColor(1, 2, 3)
    cfgGl.setTheme(config.THEME_DARK)
    cfgGl.noteColor = util.MyColor(4, 5, 6)

    cfgGl2 = newCfgGl()
    cfgGl2.load(cfgGl.save())

    assert cfgGl2.theme == config.THEME_DARK
    assert rgb(cfgGl2.noteColor) == (4, 5, 6)

    cfgGl2.setTheme(config.THEME_LIGHT)
    assert rgb(cfgGl2.noteColor) == (1, 2, 3)


def testOldConfigLoadsAsLight():
    # a config saved before themes: no Theme, unprefixed colors
    cfgGl = newCfgGl()
    cfgGl.load("Color/TextFG:10,20,30\n")

    assert cfgGl.theme == config.THEME_LIGHT
    assert rgb(cfgGl.textColor) == (10, 20, 30)

    cfgGl.setTheme(config.THEME_DARK)
    assert rgb(cfgGl.textColor) == config.DARK_COLORS["textColor"]


def testLightColorsSavedUnderOriginalNames():
    cfgGl = newCfgGl()
    cfgGl.setTheme(config.THEME_DARK)
    s = cfgGl.save()

    assert "Theme:1\n" in s
    assert "Color/TextBG:255,255,255\n" in s
    assert "Dark/Color/TextBG:30,30,30\n" in s


def testThemeDefaults():
    cfgGl = newCfgGl()

    assert rgb(cfgGl.getThemeDefault(config.THEME_LIGHT, "cursorColor")) == (
        135,
        135,
        253,
    )
    assert (
        rgb(cfgGl.getThemeDefault(config.THEME_DARK, "cursorColor"))
        == config.DARK_COLORS["cursorColor"]
    )


# WCAG 2 contrast ratio of two (r, g, b) colors
def contrast(c1, c2):
    def lum(c):
        def ch(v):
            v /= 255

            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

        r, g, b = map(ch, c)

        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1, l2 = sorted((lum(c1), lum(c2)), reverse=True)

    return (l1 + 0.05) / (l2 + 0.05)


def testDarkContrast():
    d = config.DARK_COLORS

    # text over each background it is drawn on (trelbyctrl.paint,
    # drawAutoComp; misc.MyTabCtrl2)
    pairs = [
        ("textColor", "textBgColor"),
        ("textColor", "noteColor"),
        ("textColor", "selectedColor"),
        ("textColor", "cursorColor"),
        ("textHdrColor", "textBgColor"),
        ("autoCompFgColor", "autoCompBgColor"),
        ("tabTextColor", "tabBarBgColor"),
        ("tabTextColor", "tabNonActiveBgColor"),
        ("tabTextColor", "workspaceColor"),
    ]

    for t in config.getTIs():
        pairs.append(("text%sColor" % t.name, "textBgColor"))

    pairs.append(("textNoteColor", "noteColor"))

    for fg, bg in pairs:
        assert contrast(d[fg], d[bg]) >= 4.5, (fg, bg)
