import codecs
import os
import subprocess
from Tier import Tier
from Interval import Interval
from operator import itemgetter, attrgetter
from numpy import array as nparray
from praatNumericParser import parse as numParse
from praatPitchParser import parse as pitchParse


class Grid(object):

    """docstring for Grid
    A class for storing a Praat TextGrid and performing data transformations
    and anlyses. """

    def __init__(self, xmin, xmax, size, nid, wav=False):
        super(Grid, self).__init__()
        self.xmin = xmin
        self.xmax = xmax
        self.size = size
        self.tiers = []
        self.id = nid
        self.resize()
        self.tidx = {}
        self.wav = wav

    def __str__(self):
        """Defining print function. Use for diagnostics"""
        print("\nTextGrid info:")
        print("ID: ", self.id)
        print("Grid start: ", self.xmin)
        print("Grid end: ", self.xmax)
        print("Number of tiers: ", self.size)
        print("Current number of tiers: ", self.currentsize)

        print("\nCurrent tiers:\n")

        for t in self.tiers:
            print(t.id)

        return ''

    def __getitem__(self, key):
        return self.tidx[key]

    def keys(self):
        """Returns a list of the names of the Tier objects in the Grid"""
        return self.tidx.keys()

    def addTier(self, newtier):
        """Add a tier to the grid and update the grid size."""
        self.tiers.append(newtier)
        self.tidx[newtier.id] = newtier
        self.resize()

    def addWav(self, fp):
        """Associate a wav file to the Grid object."""
        assert os.path.exists(fp) == True
        self.wav = fp

    def resize(self):
        """Update grid size."""
        self.currentsize = len(self.tiers)

    def printGrid(self, filename, rmtiernames=[]):
        """Print function to output a TextGrid to load into praat."""
        if type(filename) == str:
            fout = codecs.open(filename, 'w', 'utf8')
        else:
            fout = filename

        tierFilter = [self.getTier(x) for x in rmtiernames]
        tiers = [x for x in self.tiers if x not in tierFilter]
        header = ['File type = "ooTextFile"',
                  'Object class = "TextGrid"',
                  '',
                  'xmin = ' + str(self.xmin),
                  'xmax = ' + str(self.xmax),
                  'tiers? <exists>',
                  'size = ' + str(len(tiers)),
                  'item []:'
                  ]

        fout.write("\n".join(header) + '\n')

        for n, t in enumerate(tiers):
            fout.write(' ' * 4 + 'item [' + str(n + 1) + ']:\n')
            t.printGrid(fout)

        fout.close()

    def getTier(self, name):
        """Method to retrieve a tier by id ( which is a name ) .
        Replaced by the __getitem__() function, but kept for convenience"""
        return self.tidx[name]

    def extractTier(self, srcTiername, name, symbol):
        """Extract a tier from another tier based on the
        occurence of a substring. """

        srcTier = self.getTier(srcTiername)
        tgtTier = Tier(srcTier.xmin, srcTier.xmax, srcTier.size, name)

        for i in srcTier.intervals:
            if symbol in i.text:
                tgtTier.addInterval(i.copy('"' + symbol + '"'))
            else:
                tgtTier.addInterval(i.copy('""'))
        self.addTier(tgtTier)

    def extractMajorityTier(self, srcTiernames, name, symbol, majority):
        """Extract a tier from a set of tiers based on a majority vote of the
        occurence of the substring in $symbol."""

        ntiers = len(srcTiernames)

        # Sanity check, cannot ask for a larger majority than there are votes
        assert ntiers >= majority

        srctiers = [self.getTier(x).intervals for x in srcTiernames]
        srcMat = nparray(srctiers)
        template = self.getTier(srcTiernames[0])
        newtier = Tier(template.xmin, template.xmax, template.size, name)

        for j in range(len(srcMat[0])):
            anots = sum([1 for x in srcMat[:, j] if symbol in x.text])
            if anots >= majority:
                newtier.addInterval(template[j].copy('"' + symbol + '"'))
            else:
                newtier.addInterval(template[j].copy('""'))

        self.addTier(newtier)

    def extractSegmentTier(self, srcTiernames, name, symbol, majority=1):
        """Collapses adjacent intervals in a tier if they have the same
        annotation and updates the tier size. """
        assert type(srcTiernames) == list
        if len(srcTiernames) > 1:
            self.extractMajorityTier(srcTiernames, name, symbol, majority)
        else:
            self.extractTier(srcTiernames[0], name, symbol)

        self.mergeIntervals(name)

    def mergeIntervals(self, name):
        """Merges Interval objects in a specific Tier that have the same
        annotation. Designed for use with text annotation."""
        newtier = self.getTier(name)
        seed = newtier[0]
        newIntervals = []
        for n in range(1, newtier.currentsize):
            if seed.text == newtier[n].text:
                seed = seed.merge(newtier[n], seed.text)
            else:
                newIntervals.append(seed)

                # Use copy(), otherwise intervals are passed by reference
                seed = newtier[n].copy()
        newtier.resize(newIntervals)

    def confusionMatrixPair(self, tier1, tier2):
        """Computes the confusion pairs between a pair of tiers."""
        assert tier1.size == tier2.size
        assert tier1.currentsize == tier2.currentsize

        confusiontbl = {}
        for n, i in enumerate(tier1.intervals):
            key = tuple(sorted([i.text, tier2[n].text]))
            confusiontbl[key] = confusiontbl.get(key, 0) + 1

        return confusiontbl

    def confusionMatrix(self, tiernames, filename):
        """Computes the confusion pairs between an arbitrary # of tiers."""
        mat = {}
        ntiers = len(tiernames)
        # for each tier to compare
        for i in range(ntiers):
            # foreach tier that is not $i and has not already been compared
            for j in range(i, ntiers):
                t1 = self.tidx[tiernames[i]]
                t2 = self.tidx[tiernames[j]]
                ctbl = self.confusionMatrixPair(t1, t2)
                for k in ctbl.keys():
                    mat[k] = mat.get(k, 0) + ctbl[k]

        self.printCMatrix(mat, filename)

    def printCMatrix(self, tbl, filename, sep='\t'):
        """Prints a confusion matrix to be loaded by praat."""
        fout = codecs.open(filename, 'w', 'utf8')
        columns = ('A1', 'A2', 'Count')
        fout.write(sep.join(columns) + '\n')
        lines = []
        for k, v in tbl.items():
            lines.append([k[0], k[1], v])

        for l in sorted(lines, key=itemgetter(2), reverse=True):
            l[2] = str(l[2])
            fout.write(sep.join(l) + '\n')

        fout.close()

    def maceTiers(self, tiernames, filename, sep=','):
        """Output tiers as comma-separated lines into a csv file for Mace."""
        annotations = []
        for t in tiernames:
            tier = self.getTier(t).intervals
            annotations.append([x.text for x in tier])

        fout = codecs.open(filename, 'w', 'utf8')

        first = len(annotations[0])
        for i in range(1, len(annotations)):
            assert first == len(annotations[i])

        for i in range(first):
            fout.write(sep.join([x[i] for x in annotations]) + '\n')

        fout.close()

    def mace(self, tiernames, filename, macepath, macetiername):
        """Wrapper for Mace """

        self.maceTiers(tiernames, filename, sep=',')
        # outputs prediction and competence
        print('Running Mace ...')
        cmd = [macepath, filename]
        subprocess.call(cmd, stderr=subprocess.DEVNULL)
        print('Mace terminated.')

        template = self.getTier(tiernames[0])
        macetier = Tier(template.xmin, template.xmax,
                        template.size, macetiername)

        # Create a tier with Mace predictions
        pred = codecs.open('prediction', 'r', 'utf8')
        n = 0
        for l in pred:
            macetier.addInterval(template[n].copy(replace=l.strip()))
            n += 1
        pred.close()
        self.addTier(macetier)

        # Add competence estimates to tiers
        comp = codecs.open('competence', 'r', 'utf8').read().split()
        n = 0
        for t in tiernames:
            tier = self.getTier(t)
            tier.competence = comp[n]
            n += 1

    def downsample(self, snd=False, samplerate=16):
        """Create a new file that is a downsampling of another file.
        Assumes that $sndfile is in a higher sampling rate than
        $samplerate."""

        if snd:
            assert os.path.exists(snd) == True
        else:
            snd = self.wav
    
        stem, ext = os.path.splitext(snd)
        assert ext == '.wav'

        s = str(samplerate)
        hz = s + 'k'
        newsound = stem + '_' + hz + ext

        cmd = ['sox', snd, '-r', hz, '-b', s, '-c', '1', newsound]

        try:
            subprocess.call(cmd)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                sys.exit('Could not find ' + snd + '. Terminate.')
            else:
                print('Is SoX available on your system?')
                sys.exit('Could not downsample ' + snd + '. Terminate.')

        self.addWav(newsound)

    def hnrTier(self, praatscript, snd=False, outputdir=False,
                downsample=False):
        """Extracts harmonics-to-noise ratio using Praat. Assumes that the user
        knows the number of channels and chooses and appropriate praat script.
        If you run out of memory, use self.downsample() and specify a lower
        samplerate."""

        if snd:
            # Check arguments
            assert os.path.exists(snd) == True
            self.wav = snd
        
        if downsample:
            self.downsample(self.wav, samplerate=downsample)

        assert os.path.exists(praatscript) == True

        # Create arguments for system call
        path, filename = os.path.split(self.wav)
        stem, ext = os.path.splitext(filename)
        assert ext == '.wav'

        # Set paths
        if path == '':
            praatpath = '.'
        else:
            praatpath = os.path.abspath(path)
        if not outputdir:
            outputdir = praatpath

        hnrfile = os.path.join(outputdir, stem + '_HNR.dat')

        # File exists skip computation
        if os.path.exists(hnrfile):
            pass
        else:
            # Assume the file extension correctly indicates the encoding
            subprocess.call(['praat', praatscript, praatpath, stem, outputdir])

        # Read the Harmonicity 2 object file
        hnr = codecs.open(hnrfile, 'r', 'utf8')
        self.addTier(numParse(hnr))

    def intensityTier(self, praatscript, sndfile, outputdir=False,
                      downsample=False):
        """Adds a Tier object containing intensity measuers in dB. Use with
        Praat Intensity 2 objects."""
        assert os.path.exists(praatscript) == True
        assert os.path.exists(sndfile) == True

        if snd:
            # Check arguments
            assert os.path.exists(snd) == True
            self.wav = snd
        
        if downsample:
            self.downsample(self.wav, samplerate=downsample)

        # Create arguments for system call
        path, filename = os.path.split(self.wav)
        stem, ext = os.path.splitext(filename)
        assert ext == '.wav'

        # Set paths
        if path == '':
            praatpath = '.'
        else:
            praatpath = os.path.abspath(path)
        if not outputdir:
            outputdir = praatpath

        intfile = os.path.join(outputdir, stem + '_INT.dat')

        # Skip computation if file exists from a previous iteration
        if os.path.exists(intfile):
            pass
        else:
            subprocess.call(['praat', praatscript, praatpath, stem, outputdir])

        # Assume the file extension correctly indicates the encoding
        intensity = codecs.open(intfile, 'r', 'utf8')
        self.addTier(numParse(intensity))

    def pitchIntTier(self, praatscript, sndfile, outputdir=False,
                     downsample=False):
        """Extracts the estimated pitch and intensity (amplitude) from a
        praat Pitch 1 object. If arguments to this praat script and the
        praat script in self.hnrTier() are the same, the Interval objects will
        align."""
        assert os.path.exists(praatscript) == True
        if sndfile:
            assert os.path.exists(sndfile) == True
            self.wav = sndfile

        # Create arguments for system call
        path, filename = os.path.split(self.wav)
        stem, ext = os.path.splitext(filename)
        assert ext == '.wav'

        # Set paths
        if path == '':
            praatpath = '.'
        else:
            praatpath = os.path.abspath(path)
        if not outputdir:
            outputdir = praatpath

        pitchfile = os.path.join(outputdir, stem + '_PtR.dat')

        # Skip computation if file exists from a previous iteration
        if os.path.exists(pitchfile):
            pass
        else:
            subprocess.call(['praat', praatscript, praatpath, stem, outputdir])

        # Assume the file extension correctly indicates the encoding
        pitch = codecs.open(pitchfile, 'r', 'utf8')
        (pitchTier, intTier) = pitchParse(pitch)
        self.addTier(intTier)
        self.addTier(pitchTier)

    def timeSliceTier(self, tiername, start, end=False):
        """Finds the Interval object(s) at the specified time (interval)"""

        try:
            start = float(start)
            if end:
                end = float(end)
        except:
            if end:
                sys.exit("Cannot convert " + str(start) +
                         " and " + str(end) + " to floats. Terminate")
            else:
                sys.exit("Cannot convert " + str(
                    start) + " to float. Terminate")

        return self[tiername].timedInterval(start, end)

    def prediction(self, srcTier, tiername, annotation):
        """Test to find places with no stød
        Conditions: silence
                                +20 hnr
                                ...
        """
        try:
            pitchTier = self['"Pitch 1"']
            hnrTier = self['"Harmonicity 2"']
            intTier = self['"Intensity"']
        except:
            sys.exit('Could not retrieve necessary Tier objects. Terminate')

        predTier = Tier(hnrTier.xmin, hnrTier.xmax, hnrTier.size, tiername)
        for i in range(hnrTier.currentsize):
            if hnrTier[i].text == '"-200"':
                predTier.addInterval(hnrTier[i].copy(replace='""'))
            elif float(hnrTier[i].text.strip('"')) > 20:
                predTier.addInterval(hnrTier[i].copy(replace='""'))
            else:
                predTier.addInterval(hnrTier[i].copy(replace=annotation))

        self.addTier(predTier)
        self.mergeIntervals(tiername)




# TODO:
#
