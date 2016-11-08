import codecs
import os
import sys
import subprocess
from Tier import Tier
from praatparser import parse as gridParse
from praatNumericParser import parse as numParse
from praatPitchParser import parse as pitchParse
from praatMfccParser import parse as mfccParse
from operator import itemgetter, attrgetter
from multiprocessing import Pool
from TextGrid import Grid
from re import sub

SCRIPT = '[Danpass.py]: '

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
        # Number of available cores are detected automatically
        self.pool = Pool(6)
        self.loadCorpus(corpuspath)

    def __str__(self):
        """Defining print function. Use for diagnostics"""
        print("\nDanPASS info:")
        print("Number of grids: ", self.ngrids)

        print("\nCurrent grids:")

        for t in self.grids.keys():
            print(self[t].id)

        return ''

    def __getitem__(self, key):
        """Getter-method for textgrids"""
        return self.grids[key]

    def setOutpath(self, path=False):
        if path:
            p = os.path.join(self.corpuspath, path)
        else:
            p = os.path.join(self.corpuspath, "processed")
        return p

    def printGrids(self, filename=False, rmTiernames=[]):
        for g in self.values():
            if filename:
                g.printGrid(os.path.join(self.processedpath, filename), rmTiernames)

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

    def printKaldiData(self, path):
        text = []
        segments = []
        wav_scp = []
        utt2spk = []
        spk2utt_map = {}

        for g in self.values():
            recid = os.path.splitext(g.id)[0]
            spkid = recid.rsplit('_', 1)[0]
            gUttids, gSegments, gText, wav = g.extractKaldiData('"ortografi"',
                                                                recid)
            if spkid not in spk2utt_map:
                spk2utt_map[spkid] = []
            wav_scp.append(' '.join((recid, wav)) + '\n')
            for i in range(len(gUttids)):
                uttid = gUttids[i]
                clean_text = sub('[ =,\"+\-]', '', gText[i])
                clean_text = clean_text.replace('_', ' ').strip()
                if clean_text == '':
                    continue
                text.append(' '.join((uttid, clean_text.lower())) + '\n')
                segments.append(' '.join((uttid, recid, gSegments[i])) + '\n')
                utt2spk.append(' '.join((uttid, spkid)) + '\n')
                spk2utt_map[spkid].append(uttid)

        spk2utt = ["{0} {1}\n".format(x[0], ' '.join(x[1])) for x in spk2utt_map.items()]


        fout = open(os.path.join(path, 'text'), 'w')
        fout.writelines(sorted(text))
        fout.close()
        fout = open(os.path.join(path, 'segments'), 'w')
        fout.writelines(sorted(segments))
        fout.close()
        fout = open(os.path.join(path, 'wav.scp'), 'w')
        fout.writelines(sorted(wav_scp))
        fout.close()
        fout = open(os.path.join(path, 'utt2spk'), 'w')
        fout.writelines(sorted(utt2spk))
        fout.close()
        fout = open(os.path.join(path, 'spk2utt'), 'w')
        fout.writelines(sorted(spk2utt))
        fout.close()

    def extractTiers(self, srcTiername, name, symbol):
        """Calls the same extractTier method on all grids in the object"""
        for g in self.values():
            g.extractTier(srcTiername, name, symbol)

    def extractMajorityTiers(self, srcTiernames, name, symbol, majority):
        """Calls the same extractMajorityTier method on all grids in the object"""
        for g in self.values():
            g.extractTier(srcTiername, name, symbol, majority)

    def extractSegmentTiers(self, srcTiernames, name, symbol, majority=1):
        """Calls the same extractSegmentTier method on all grids in the object"""
        for g in self.values():
            g.extractSegmentTier(srcTiernames, name, symbol, majority)

    def pitchIntTiers(self, praatscript, sndfile, downsample=False):
        """Calls the same pitchIntTier method on all grids in the object. Should be
        parallelised"""
        for g in self.values():
            g.pitchIntTier(
                praatscript, sndfile, self.processedpath, downsample)

    def globalDownsample16(self, overwrite=False):
        """Parallelised downsampling method that downsamples to 16k only"""
        grids = sorted(self.values(), key=attrgetter('id'))
        wavs = [(x.wav, self.processedpath, overwrite) for x in grids]
        #pairs = [(x, self.processedpath) for x in wavs]

        downsampled = sorted(self.pool.map(downsample16, wavs))

        for g, w in zip(grids, downsampled):
            fname = os.path.split(w)[-1]
            newsound = os.path.join(self.processedpath, fname)
            os.rename(w, newsound)
            g.addWav(newsound)

    def extractHnrTiers(self, praatscript, override=False, downsample=False):
        """Computes harmonics-to-noise ratio using praat. Downsamples if
        specified, overwrites existing files if specified."""
        suffix = '_HNR.dat'
        if downsample:
            self.globalDownsample16()
        assert os.path.exists(praatscript) == True
        args = []
        for g in self.values():
            path, filename = os.path.split(g.wav)
            stem, ext = os.path.splitext(filename)

            # Set paths
            if path == '':
                praatpath = '.'
            else:
                praatpath = os.path.abspath(path)

            # The computation is time consuming (~21m/4 cores). If the file
            # exists, do not repeat computation unless explicitly specified
            # with $override
            g.hnrfile = os.path.join(self.processedpath, stem + suffix)
            if os.path.exists(g.hnrfile) and override == False:
                pass
            else:
                args.append(
                    [praatscript, praatpath, stem, self.processedpath])

        if len(args) == 2:
            processedfiles = featureExtraction(args[0])
        else:
            processedfiles = self.pool.map(featureExtraction, args)
        processedfiles = self.pool.map(featureExtraction, args)

        for g in self.values():
            g.addTier(numParse(codecs.open(g.hnrfile, 'r', 'utf8')))

    def extractPitchIntTiers(self, praatscript, override=False, downsample=False):
        """Computes F0 using praat and extracts intensity too. Downsamples if
        specified, overwrites existing files if specified."""
        suffix = '_PtR.dat'
        if downsample:
            self.globalDownsample16()
        assert os.path.exists(praatscript) == True
        args = []
        for g in self.values():
            path, filename = os.path.split(g.wav)
            stem, ext = os.path.splitext(filename)

            # Set paths
            if path == '':
                praatpath = '.'
            else:
                praatpath = os.path.abspath(path)

            # The computation is time consuming (~21m/4 cores). If the file
            # exists, do not repeat computation unless explicitly specified
            # with $override
            g.pitchfile = os.path.join(self.processedpath, stem + suffix)
            if os.path.exists(g.pitchfile) and override == False:
                pass
            else:
                # Pack arguments in a list. multiprocessing.pool.starmap was
                # implemented in py3.3 which is not installed on current
                # Ubuntu LTS
                args.append(
                    [praatscript, praatpath, stem, self.processedpath])

        if len(args) == 1:
            processedfiles = featureExtraction(args[0])
        else:
            processedfiles = self.pool.map(featureExtraction, args)

        for g in self.values():
            (pitchTier, intTier) = pitchParse(
                codecs.open(g.pitchfile, 'r', 'utf8'))
            g.addTier(intTier)
            g.addTier(pitchTier)

    def extractMfccTiers(self, praatscript, override=False, downsample=False):
        """Computes F0 using praat and extracts intensity too. Downsamples if
        specified, overwrites existing files if specified."""
        suffix = '_MFCC.dat'
        if downsample:
            self.globalDownsample16()
        assert os.path.exists(praatscript) == True
        args = []
        for g in self.values():
            path, filename = os.path.split(g.wav)
            stem, ext = os.path.splitext(filename)

            # Set paths
            if path == '':
                praatpath = '.'
            else:
                praatpath = os.path.abspath(path)

            # The computation is time consuming (~21m/4 cores). If the file
            # exists, do not repeat computation unless explicitly specified
            # with $override
            g.mfccfile = os.path.join(self.processedpath, stem + suffix)
            if os.path.exists(g.mfccfile) and override == False:
                pass
            else:
                # Pack arguments in a list. multiprocessing.pool.starmap was
                # implemented in py3.3 which is not installed on current
                # Ubuntu LTS
                args.append(
                    [praatscript, praatpath, stem, self.processedpath])

        if len(args) == 1:
            processedfiles = featureExtraction(args[0])
        else:
            processedfiles = self.pool.map(featureExtraction, args)

        for g in self.values():
            mfccTier = mfccParse(
                codecs.open(g.mfccfile, 'r', 'utf8'))
            g.addTier(mfccTier)

    def MLdataFromTiers(self, tgtTier, write=False, tbl_id=False):
        """Method to convert information in Tier objects to vectors for
        training ML models. The source Tiers that provide training data is
        hard-coded because they need special treatment."""
        args = []
        grids = self.values()
        for g in grids:
            args.append((g, tgtTier))
        datatbls = self.pool.map(alignDataFromTiers, args)
        print(SCRIPT + "Data resegmentation complete", "...")
        assert len(grids) == len(datatbls)
        if tbl_id == False:
            tbl_id = ''
        elif tbl_id[0] == '"' and tbl_id[-1] == '"':
            # if tbl_id is a Tier name
            tbl_id = '.' + tbl_id[1:-1]
        else:
            # base case
            tbl_id = '.' + tbl_id

        if write:
            writeArgs = []
            for tbl, g in zip(datatbls, grids):
                path = os.path.join(self.processedpath,
                           os.path.splitext(g.id)[0] + tbl_id + '.tbl')
                writeArgs.append((tbl, path))
            res = self.pool.map(writeTable, writeArgs)
        else:
            for tbl, g in zip(datatbls, grids):
                g.mltbl = tbl

    def splitAnnotation(self, srcTiername, tgtTiername):
        """Method that splits annotation in Interval objects"""
        args = [(x, srcTiername, tgtTiername) for x in self.values()]
        res = self.pool.map(splitSyllables, args)
        for g, t in zip(self.values(), res):
            g.addTier(t)

    def addMLTier(self, gridname, tgtTiername, tblfile, duration=0.005, mapping=False):
        """Adds a new tier to a named grid from a table file. The table file
        is usually output from a ML algorithm but can be any list"""
        assert os.path.exists(tblfile) == True
        self[gridname].loadPrediction(tblfile, tgtTiername,
            duration=duration, mapping=mapping)



# Functions used by DanPASS class
# The computation handled in these functions are functions and not class
# because the class methods cannot be pickled and therefore not passed to the
# processing pool.

def splitSyllables(args):
    """Splits annotation of Interval objects. Currently configured for DanPASS
    annotation."""
    glueleft = set([':', 'ˀ', '̩', 'ː', '̯ˀ', '̯'])
    glueright = set(["'", 'ˈ'])
    grid, src, tgt = args
    srcTier = grid[src]
    tgtIntervals = srcTier.splitText(tgt, glueleft, glueright)
    tgtTier = Tier(srcTier.xmin, srcTier.xmax, len(tgtIntervals), tgt)
    tgtTier.resize(tgtIntervals)
    return tgtTier


def alignDataFromTiers(args):
    """Splits and aligns data int tiers so the segmentation is identical. """
    grid, tgtTiername = args
    print(SCRIPT + "Aligning", grid.id + ".")
    names = ['"Harmonicity 2"', '"MFCC"', tgtTiername]
    data = []
    for i, j in zip(grid['"Pitch 1"'], grid['"Intensity"']):
        point = [str(i.xmin), str(i.xmax), i.text, j.text]
        othertiers = [x.getText() for x in grid.timeSliceTiers(names, i.xmin)]
        data.append(point + othertiers)
    return data


def writeTable(args):
    """Writes the data tables extracted from Tier objects to file."""
    list_of_lists, path = args
    gdata = codecs.open(path, 'w', 'utf8')
    for l in list_of_lists:
        gdata.write('\t'.join(l) + "\n")
    gdata.close()


def featureExtraction(args):
    """Extracts the harmonics-to-noise tier information from a sound file and
    returns the name of the extracted hnr file. Computation is costly and
    therefore reports when a file has been processed."""
    cmd = ["praat"]
    cmd.extend(args)
    ret = subprocess.call(cmd)
    featurefile = os.path.join(args[-1], args[-2])
    try:
        assert ret == 0
    except AssertionError:
        sys.exit(SCRIPT + "Processing of " + str(featurefile) + " failed.")
    print(SCRIPT + "Processing of", featurefile, "completed.")
    return featurefile


def downsample16(args):
    """Takes an input file and an output path and passes it to SoX. A few
    samples are clipped."""
    wav, outpath, mode = args
    s = '16'
    hz = s + 'k'
    stem, ext = os.path.splitext(wav)
    newsndfile = os.path.split(stem)[-1] + '_' + hz + ext
    newsoundpath = os.path.join(outpath, newsndfile)
    if os.path.exists(newsoundpath) and mode == False:
        pass
    else:
        cmd = ['sox', wav, '-r', hz, '-b', s, '-c', '1', newsoundpath]
        subprocess.call(cmd)
    return newsoundpath
