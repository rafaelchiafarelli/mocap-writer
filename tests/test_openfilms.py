# bugs/editor/20: the window keeps every open film, and a tab belongs to
# the film whose script it holds (trelby/openfilms.py, MyFrame.showFilm,
# MyCtrl.openFilm)

import tests.u as u  # first: trelby.util cannot be the first trelby module loaded
import trelby.film as film
import trelby.openfilms as openfilms
import trelby.trelbyctrl as trelbyctrl
import trelby.trelbyframe as trelbyframe


def setup_module():
    u.init()


def twoFilms(tmp_path):
    films = openfilms.OpenFilms()
    a = films.add(film.Film.create(tmp_path / "a", "INT. A - DAY #1#\n"))
    b = films.add(film.Film.create(tmp_path / "b", "INT. B - DAY #1#\n"))

    return films, a, b


def test_a_script_finds_its_own_film(tmp_path):
    films, a, b = twoFilms(tmp_path)

    assert films.withScript(str(a.film.partPath("script"))) is a
    assert films.withScript(str(b.film.partPath("script"))) is b
    assert films.withScript(str(tmp_path / "other.fountain")) is None
    assert films.withScript(None) is None
    assert films.at(tmp_path / "a" / ".") is a


def test_opening_a_film_again_replaces_it(tmp_path):
    films, a, _b = twoFilms(tmp_path)
    again = films.add(film.Film.open(tmp_path / "a"))

    assert again is not a
    assert films.at(tmp_path / "a") is again
    assert len(films.films) == 2


class FakeCtrl:
    def __init__(self, fileName):
        self.fileName = fileName
        self.fileNameDisplay = str(fileName)

    def SetFocus(self):
        pass

    def updateCommon(self):
        pass


class FakePanel:
    def __init__(self, ctrl):
        self.ctrl = ctrl


class FakeTabCtrl:
    def __init__(self, panels):
        self.panels = panels

    def getPage(self, i):
        return self.panels[i]


class FakeBiblePanel:
    def __init__(self):
        self.bible = None

    def setBible(self, b):
        self.bible = b

    def changed(self):
        pass


class FakeFrame:
    filmOf = trelbyframe.MyFrame.filmOf
    showFilm = trelbyframe.MyFrame.showFilm

    def __init__(self, films, fileNames):
        self.openFilms = films
        self.tabCtrl = FakeTabCtrl([FakePanel(FakeCtrl(n)) for n in fileNames])
        self.panel = self.tabCtrl.getPage(0)
        self.biblePanel = FakeBiblePanel()
        self.film = self.bible = self.annotations = None
        self.filmListeners = []

    def setTitle(self, text):
        pass


# the bug: with two films open, the first film's tab showed the second
# film's bible
def test_switching_tabs_switches_the_film(tmp_path):
    films, a, b = twoFilms(tmp_path)
    frame = FakeFrame(
        films,
        [str(a.film.partPath("script")), str(b.film.partPath("script")), None],
    )

    for page, of in [(1, b), (0, a), (1, b)]:
        trelbyframe.MyFrame.OnPageChange(frame, page)

        assert frame.film is of.film
        assert frame.bible is of.bible
        assert frame.annotations is of.annotations
        assert frame.biblePanel.bible is of.bible

    # a script of no film shows no bible, so nothing is written into the
    # last film's
    trelbyframe.MyFrame.OnPageChange(frame, 2)

    assert frame.film is None and frame.biblePanel.bible is None


class FakeSp:
    def __init__(self, moves):
        self.sceneMoves = moves


class FakeGd:
    def __init__(self, frame):
        self.mainFrame = frame


class SavingCtrl:
    openFilm = trelbyctrl.MyCtrl.openFilm
    renameFilmScenes = trelbyctrl.MyCtrl.renameFilmScenes

    def __init__(self, frame, fileName, moves):
        self.gd = FakeGd(frame)
        self.fileName = fileName
        self.sp = FakeSp(moves)


# Save on exit saves a tab that is not the current one: its scene moves go
# to its own film's records, not the current film's
def test_a_save_writes_its_own_films_records(tmp_path):
    films, a, b = twoFilms(tmp_path)
    setA = a.bible.create("set", "A")
    a.bible.link(setA, "1")
    setB = b.bible.create("set", "B")
    b.bible.link(setB, "1")

    frame = FakeFrame(films, [str(b.film.partPath("script"))])
    trelbyframe.MyFrame.OnPageChange(frame, 0)
    SavingCtrl(frame, str(a.film.partPath("script")), {"1": "2"}).renameFilmScenes()

    assert sorted(a.bible.scenes(setA)) == ["2"]
    assert sorted(b.bible.scenes(setB)) == ["1"]
