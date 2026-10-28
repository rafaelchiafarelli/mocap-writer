import trelby.scenenumbers as sn

# the numbering rule (fountain-native/scenes/1): permanent numbers, letters
# for inserts, levels alternating number and letter.


def testParse():
    assert sn.parse("12") == (12,)
    assert sn.parse("12.A") == (12, "A")
    assert sn.parse("12.A.1.B") == (12, "A", 1, "B")

    for bad in ("", None, "0", "012", "12A", "1A", "I-1-A", "12.a", "12.AB",
                "12.A.0", "12.1", "12.", ".12", "A"):
        assert sn.parse(bad) is None, bad


def testFmt():
    assert sn.fmt((12, "A", 1)) == "12.A.1"


def testKeyOrder():
    order = ["1", "2", "12", "12.A", "12.A.1", "12.A.1.A", "12.A.2", "12.B",
             "12.Z", "12.Z.1", "13"]

    assert sorted(order, key=sn.key) == order


def testFreshScript():
    assert sn.assign([None, None, None]) == (["1", "2", "3"], [])
    assert sn.assign([]) == ([], [])


def testAppend():
    assert sn.assign(["1", "2", None]) == (["1", "2", "3"], [])
    assert sn.assign(["1", "2", None, None]) == (["1", "2", "3", "4"], [])

    # after the highest, even when the last one is a lettered insert
    assert sn.assign(["1", "1.A", None]) == (["1", "1.A", "2"], [])


def testInsertAfterWholeNumber():
    assert sn.assign(["12", None, "13"]) == (["12", "12.A", "13"], [])

    # a whole number never gets the next whole number in the middle, even
    # when it is free
    assert sn.assign(["12", None, "15"]) == (["12", "12.A", "15"], [])


def testInsertAfterLetter():
    assert sn.assign(["12", "12.A", None, "13"]) == (
        ["12", "12.A", "12.B", "13"],
        [],
    )


def testNested():
    assert sn.assign(["12.A", None, "12.B"]) == (["12.A", "12.A.1", "12.B"], [])
    assert sn.assign(["12.A.1", None, "12.A.2"]) == (
        ["12.A.1", "12.A.1.A", "12.A.2"],
        [],
    )

    # a nested number's sibling, when it is the last child
    assert sn.assign(["12.A.1", None, "12.B"]) == (
        ["12.A.1", "12.A.2", "12.B"],
        [],
    )


def testAfterZ():
    assert sn.assign(["12.Z", None, "13"]) == (["12.Z", "12.Z.1", "13"], [])


def testSeveralInARow():
    assert sn.assign(["12", None, None, None, "13"]) == (
        ["12", "12.A", "12.B", "12.C", "13"],
        [],
    )
    assert sn.assign(["12.A", None, None, "12.B"]) == (
        ["12.A", "12.A.1", "12.A.2", "12.B"],
        [],
    )


def testNoRoom():
    # between a scene and its first child
    assert sn.assign(["12", None, "12.A"]) == (["12", None, "12.A"], [1])
    assert sn.assign(["12.A", None, None, "12.A.1"]) == (
        ["12.A", None, None, "12.A.1"],
        [1, 2],
    )

    # before the first numbered scene
    assert sn.assign([None, "1"]) == ([None, "1"], [0])

    # after, or before, another tool's form
    assert sn.assign(["1A", None, "2"]) == (["1A", None, "2"], [1])
    assert sn.assign(["1", None, "1B"]) == (["1", None, "1B"], [1])

    # at the end too
    assert sn.assign(["1", "1B", None]) == (["1", "1B", None], [2])


def testNumbersNeverChange():
    nums = ["1", "2", "2.A", "3"]

    assert sn.assign(nums)[0] == nums
    assert sn.assign(["1", None, "2", "3"])[0][::2] == ["1", "2"]


def testCheck():
    P = sn.Problem

    assert sn.check(["1", "2", "2.A", "3"]) == []
    assert sn.check(["1", "2", "2"]) == [P(sn.PROBLEM_DUPLICATE, 2, "2")]
    assert sn.check(["1", "3", "2"]) == [P(sn.PROBLEM_ORDER, 2, "2")]
    assert sn.check(["1", "1A"]) == [P(sn.PROBLEM_FOREIGN, 1, "1A")]
    assert sn.check(["1", None, ""]) == [
        P(sn.PROBLEM_MISSING, 1, ""),
        P(sn.PROBLEM_MISSING, 2, ""),
    ]
