# an import that ends in a complete film (import-to-film), no wx: the
# original file copied into the film.

import os
import shutil

SOURCE_PART = "source"
SOURCE_PATH = "source/"


# copy the imported file into the film's source part (added when the film
# has none); returns its path relative to the film root
def copySource(f, path):
    if f.part(SOURCE_PART) is None:
        f.addPart(SOURCE_PART, SOURCE_PATH)

    rel = f.part(SOURCE_PART).path.rstrip("/") + "/" + os.path.basename(path)
    f.checkWrite(rel)
    (f.root / rel).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, f.root / rel)

    return rel
