# the films open in the window (bugs/editor/20): each with its bible and
# annotations, kept by its root's real path. a tab belongs to the film whose
# script it holds, so switching tabs switches the film, and a save looks up
# its own film rather than the current tab's. no wx.

import os

import trelby.annotations as annotations
import trelby.bible as bible


class OpenFilm:
    def __init__(self, f):
        self.film = f
        self.bible = bible.Bible(f)
        self.annotations = annotations.Annotations(f)

    # read the bible and the annotations again (after the relink dialog)
    def reload(self):
        self.bible = bible.Bible(self.film)
        self.annotations = annotations.Annotations(self.film)


def key(path):
    return os.path.realpath(str(path))


class OpenFilms:
    def __init__(self):
        # key(root) -> OpenFilm
        self.films = {}

    # open f, replacing a film already open from the same root
    def add(self, f):
        of = OpenFilm(f)
        self.films[key(f.root)] = of

        return of

    # the open film at root, or None
    def at(self, root):
        return self.films.get(key(root))

    # the open film whose script is fileName, or None
    def withScript(self, fileName):
        if not fileName:
            return None

        k = key(fileName)

        for of in self.films.values():
            if key(of.film.partPath("script")) == k:
                return of

        return None
