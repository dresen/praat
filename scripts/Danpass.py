import codecs
import os
import sys
import subprocess
from praatparser import parse as gridParse
from operator import itemgetter, attrgetter
from multiprocessing import Pool
from TextGrid import Grid


class DanPASS(object):

    """docstring for DanPASS"""

    def __init__(self, corpuspath, outpath=False):
        super(DanPASS, self).__init__()
        self.corpuspath = corpuspath
        if not outpath:
            self.processedpath = self.setOutpath()
        else:
            self.processedpath = outpath
        if not os.path.exists(self.processedpath):
            os.mkdir(self.processedpath)
        self.grids = {}
        self.ngrids = 0
        self.pool = Pool(4)
        self.loadCorpus(corpuspath)

    def __str__(self):
        """Defining print function. Use for diagnostics"""
        print("\nDanPASS info:")
        print("Number of grids: ", self.ngrids)

        print("\nCurrent grids:")

        for t in self.grids.keys():
            print(self[t])

        return ''

    def __getitem__(self, key):
        """Getter-method for textgrids"""
        return self.grids[key]

    def setOutpath(self):
        p = os.path.join(self.corpuspath, "processed")
        return p

    def printGrids(self, rmTiernames=[]):

        for g in self.values():
            g.printGrid(os.path.join(self.processedpath, g.id), rmTiernames)

    def keys(self):
        return self.grids.keys()

    def values(self):
        return self.grids.values()

    def addGrid(self, textgrid, sndfile=False):
        """Setter-method for textgrids"""
        if sndfile:
            textgrid.addWav(sndfile)
        self.grids[textgrid.id] = textgrid
        textgrid.outpath = self.processedpath
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
        wavs = sorted([x for x in files if os.path.splitext(x)[1] == '.wav'])
        assert len(gridfiles) == len(wavs)

        # Heavy processing, so do it in parallel
        textgrids = self.pool.map(gridParse, gridfiles)

        for n, g in enumerate(sorted(textgrids, key=attrgetter("id"))):
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

    def extractHnrTiers(self, praatscript, replace_snd=False, downsample=False):
        for g in self.values():
            g.hnrTier(praatscript, replace_snd, self.processedpath, downsample)

    def pitchIntTiers(self, praatscript, sndfile, downsample=False):

        for g in self.values():
            g.pitchIntTier(
                praatscript, sndfile, self.processedpath, downsample)

    def globalDownsample16(self):

        grids = sorted(self.values(), key=attrgetter('id'))
        wavs = [x.wav for x in grids]

        downsampled = sorted(self.pool.map(downsample16, wavs))

        for g, w in zip(grids, downsampled):
            fname = os.path.split(w)[-1]
            newsound = os.path.join(self.processedpath, fname)
            os.rename(w, newsound)
            g.addWav(newsound)



def downsample16(wav):

        s = '16'
        hz = s + 'k'
        stem, ext = os.path.splitext(wav)
        newsound = stem + '_' + hz + ext
        cmd = ['sox', wav, '-r', hz, '-b', s, '-c', '1', newsound]
        subprocess.call(cmd)
        return newsound