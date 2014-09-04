import codecs
import os
import subprocess
from TextGrid import grid
from praatparser import parse as gridParse


class DanPASS(object):

    """docstring for DanPASS"""

    def __init__(self, corpuspath, outpath=False):
        super(DanPASS, self).__init__()
        self.corpuspath = corpuspath
        self.processedpath = outpath
        self.loadCorpus()
        self.data = {}
        self.ngrids = 0

    def __getitem__(self, key):
        """Getter-method for textgrids"""
        return self.data[key]

    def addGrid(self, filehandle, filepath):
        """Setter-method for textgrids"""
        g = gridParse(filehandle, filepath)
        self.data[grid.id] = grid
        self.ngrids += 1

    def rmGrid(self, grid):
        """To remove grids from the object"""
        del self[grid.id]
        self.ngrids -= 1

    def loadCorpus(self, path):
        """Loads a preprocessed version of DanPASS. The Textgrids have been converted to utf8 encoding using Praat."""
        assert os.path.exists(path) == True

        files = os.listdir(path)
        gridfiles = [x for x in files if os.path.splitext(x)[1] == '.TextGrid']
        wavs = [x for x in files if os.path.splitext(x)[1] == '.wav']
        assert len(grids) == len(wavs)

        for f in gridfiles:
            p = os.path.abspath(f)
            fh = codecs.open(p, 'r', 'utf8')
            self.addGrid(fh, p)
