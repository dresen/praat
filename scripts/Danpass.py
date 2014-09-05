import codecs
import os
import subprocess
from praatparser import parse as gridParse
from multiprocessing import Pool


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

    def addGrid(self, textgrid, sndfile=False):
        """Setter-method for textgrids"""
        if sndfile:
            textgrid.addWav(sndfile)
        self.grids[textgrid.id] = textgrid
        self.ngrids += 1

    def rmGrid(self, grid):
        """To remove grids from the object"""
        del self[grid.id]
        self.ngrids -= 1

    def loadCorpus(self, path):
        """Loads a preprocessed version of DanPASS. The Textgrids have been 
        converted to utf8 encoding using Praat. Only considers the monologues
        in this setup."""
        assert os.path.exists(path) == True
        path = os.path.abspath(path)
        files = [os.path.join(path, x) for x in os.listdir(path)]
        gridfiles = [x for x in files if os.path.splitext(x)[1] == '.TextGrid']
        wavs = [x for x in files if os.path.splitext(x)[1] == '.wav']
        assert len(gridfiles) == len(wavs)

        pool = Pool(processes=4)

        textgrids = pool.map(gridParse, gridfiles)
        for n, g in enumerate(textgrids):
            self.addGrid(g, wavs[n])


        #for f, w in zip(gridfiles, wavs):
        #    self.addGrid(f, w)
