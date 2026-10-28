# -*- coding: utf-8 -*-

import trelby.config as config

# constants that could not be removed yet
from trelby.screenplay import ACTION, LB_LAST


# marks a scene number in str(line): lb, lt, NUM_MARK, number, NUM_MARK,
# text. also written, with an empty number, before a text that starts with
# it, so fromStr never mistakes text for a number.
NUM_MARK = "\x01"


# one line in a screenplay
class Line:
    def __init__(self, lb=LB_LAST, lt=ACTION, text="", num=""):

        # line break type
        self.lb = lb

        # line type
        self.lt = lt

        # text
        self.text = text

        # permanent scene number ("12.A"), "" if none. kept on the first
        # line of a scene heading (fountain-native/scenes/2); it stays on
        # the line if its type changes, so changing it back restores it.
        self.num = num

    def __str__(self):
        s = config.lb2char(self.lb) + config.lt2char(self.lt)

        if self.num or self.text.startswith(NUM_MARK):
            s += NUM_MARK + self.num + NUM_MARK

        return s + self.text

    def __repr__(self) -> str:
        return self.__str__()

    def __ne__(self, other):
        return (
            (self.lt != other.lt)
            or (self.lb != other.lb)
            or (self.text != other.text)
            or (self.num != other.num)
        )

    def __eq__(self, other):
        return not self.__ne__(other)

    # opposite of __str__. NOTE: only meant for storing data internally by
    # the program! NOT USABLE WITH EXTERNAL INPUT DUE TO COMPLETE LACK OF
    # ERROR CHECKING!
    @staticmethod
    def fromStr(s):
        num = ""
        text = s[2:]

        if text.startswith(NUM_MARK):
            end = text.index(NUM_MARK, 1)
            num = text[1:end]
            text = text[end + 1 :]

        return Line(config.char2lb(s[0]), config.char2lt(s[1]), text, num)

    # a copy of the line, its scene number included
    def copy(self):
        return Line(self.lb, self.lt, self.text, self.num)
