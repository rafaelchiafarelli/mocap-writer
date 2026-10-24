import tests.u as u
import trelby.screenplay as scr


# test changing type of one element
def testChangeOneElem():
    sp = u.load()
    ls = sp.lines

    sp.cmd("moveDown")

    sp.cmd("tab")
    assert ls[1].lt == scr.CHARACTER

    sp.cmd("toPrevTypeTab")
    assert ls[1].lt == scr.ACTION

    functionMap = {
        "toScene": scr.SCENE,
        "toCharacter": scr.CHARACTER,
        "toAction": scr.ACTION,
        "toDialogue": scr.DIALOGUE,
        "toParen": scr.PAREN,
        "toShot": scr.SHOT,
        "toNote": scr.NOTE,
        "toTransition": scr.TRANSITION,
    }

    for func, ele in list(functionMap.items()):
        sp.cmd(func)

        assert ls[0].lt == scr.SCENE

        i = 1
        while 1:
            assert ls[i].lt == ele

            if ls[i].lb == scr.LB_LAST:
                break

            i += 1

        assert ls[i + 1].lt == scr.CHARACTER


# test that when text belonging to multiple elements is selected, changing
# type changes all of those elements
def testChangeManyElemes():
    sp = u.load()
    ls = sp.lines

    # select second and third elements
    sp.cmd("moveDown")
    sp.cmd("setMark")
    sp.cmd("moveDown", count=4)

    sp.cmd("toTransition")

    assert ls[0].lt == scr.SCENE

    for i in range(1, 13):
        assert ls[i].lt == scr.TRANSITION

    assert ls[11].lb == scr.LB_LAST
    assert ls[12].lb == scr.LB_LAST

    assert ls[13].lt == scr.DIALOGUE


# Tab cycles Scene -> Action -> Character -> Dialogue -> Scene and Shift+Tab
# goes back (editor-ux/typing/1). the cursor is at the start of a non-empty
# element, so Tab converts instead of creating a new element.
def testTabCycle():
    sp = u.load()
    ls = sp.lines

    sp.cmd("moveDown")
    assert ls[1].lt == scr.ACTION

    for lt in (scr.CHARACTER, scr.DIALOGUE, scr.SCENE, scr.ACTION):
        sp.cmd("tab")
        assert ls[1].lt == lt


def testShiftTabCycle():
    sp = u.load()
    ls = sp.lines

    sp.cmd("moveDown")

    for lt in (scr.SCENE, scr.DIALOGUE, scr.CHARACTER, scr.ACTION):
        sp.cmd("toPrevTypeTab")
        assert ls[1].lt == lt


# an element outside the cycle enters it at Action, both ways.
def testTabOutsideCycle():
    sp = u.load()
    ls = sp.lines

    sp.cmd("moveDown")

    for cmd in ("tab", "toPrevTypeTab"):
        sp.cmd("toTransition")
        sp.cmd(cmd)
        assert ls[1].lt == scr.ACTION
