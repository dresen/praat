import codecs
import os
import subprocess
from praatparser import parse as gridParse


class DanPASS(object):

    """docstring for DanPASS"""

    def __init__(self, corpuspath, outpath=False):
        super(DanPASS, self).__init__()
        self.corpuspath = corpuspath
        self.processedpath = outpath
        self.grids = {}
        self.ngrids = 0
        self.loadCorpus(corpuspath)
        
    def __str__(self):
        """Defining print function. Use for diagnostics"""
        print("\nDanPASS info:")
        print("Number of grids: ", self.ngrids)

        print("\nCurrent tiers:\n")

        for t in self.grids.keys():
            print(self[t])

        return ''

    def __getitem__(self, key):
        """Getter-method for textgrids"""
        return self.grids[key]

    def addGrid(self, filehandle, filepath, sndfile):
        """Setter-method for textgrids"""
        g = gridParse(filehandle, filepath)
        g.addWav(sndfile)
        self.grids[g.id] = g
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
        assert len(gridfiles) == len(wavs)

        for f, w in zip (gridfiles, wavs):
            p = os.path.join(path, f)
            wav = os.path.join(path, w)
            fh = codecs.open(p, 'r', 'utf8')
            self.addGrid(fh, p, wav)
