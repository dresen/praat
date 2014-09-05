import codecs
import os
import subprocess
from praatparser import parse as gridParse
from multiprocessing import Pool
from TextGrid import Grid


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

        print("\nCurrent grids:\n")

        for t in self.grids.keys():
            print(self[t])

        return ''

    def __getitem__(self, key):
        """Getter-method for textgrids"""
        return self.grids[key]

    def keys(self):
        return self.grids.keys()

    def values(self):
        return self.grids.values()

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

        # Heavy processing, so do it in parallel
        pool = Pool(processes=4)
        textgrids = pool.map(gridParse, gridfiles)

        for n, g in enumerate(textgrids):
            self.addGrid(g, wavs[n])

    def extractTiers(self, srcTiername, name, symbol):
        for g in self.values():
            g.extractTier(srcTiername, name, symbol)

    def extractMajorityTiers(self, srcTiernames, name, symbol, majority):
        for g in self.values():
            g.extractTier(srcTiername, name, symbol, majority)

    def extractSegmentTiers(self, srcTiernames, name, symbol, majority=1):
        for g in self.values():
            g.extractSegmentTier(srcTiernames, name, symbol, majority)

    def hnrTiers(self, praatscript, snd=False, outputdir=False,
                 downsample=False):
        for g in self.values():
            g.hnrTier(praatscript, snd, outputdir, downsample)

    def pitchIntTiers(self, praatscript, sndfile, outputdir=False,
                      downsample=False):

        for g in self.values():
            g.pitchIntTier(praatscript, sndfile, outputdir, downsample)
