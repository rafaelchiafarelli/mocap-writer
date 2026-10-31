# counting clicks (bugs/editor/14-16): wx reports a double click but no
# triple one, so the editor counts them itself, by time and place. no wx.


class ClickCounter:
    # a click within 'interval' seconds of the previous one, on the same
    # line, continues the count
    def __init__(self, interval=0.5):
        self.interval = interval
        self.count = 0
        self.time = None
        self.line = None

    # a mouse button press at time t (seconds) on line; isDouble is True
    # for the double-click event wx sends with the second press. returns
    # the click count: 1, 2, 3...
    def click(self, t, line, isDouble=False):
        near = (
            self.time is not None
            and t - self.time <= self.interval
            and line == self.line
        )

        # wxGTK sends the second press twice (a press, then the double
        # click): the double click right after a press is the same click
        if isDouble and near and t - self.time < 0.05 and self.count >= 2:
            return self.count

        self.count = self.count + 1 if near else 1

        if isDouble and self.count < 2:
            self.count = 2

        self.time = t
        self.line = line

        return self.count
