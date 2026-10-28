import trelby.pml as pml
import trelby.screenplay as screenplay


# used to iteratively add PML pages to a document
class Pager:
    def __init__(self, cfg):
        self.doc = pml.Document(cfg.paperWidth, cfg.paperHeight)

        # used in several places, so keep around
        self.charIndent = cfg.getType(screenplay.CHARACTER).indent
        self.sceneIndent = cfg.getType(screenplay.SCENE).indent

        # label of the current scene's number ("12.A", "(13)"), "" before
        # the first scene
        self.scene = ""

        # scenenumbers.labels() of the script, filled when first needed
        self.sceneLabels = None

        # number of CONTINUED:'s lines added for current scene
        self.sceneContNr = 0
