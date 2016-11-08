from Interval import Interval
import sys


class Tier(object):

    """
    A class for a Praat Tier. The class supports extraction of new tiers from
    existing Tiers and adding new Tiers from extracted Praat object as well as
    transforms on the Interval objects that are stored in a Tier object. Also
    implements a wrapper for Mace, to compute inter-annotator agreement etc."""

    def __init__(self, xmin, xmax, size, nid):
        super(Tier, self).__init__()
        self.xmin = xmin
        self.xmax = xmax
        self.size = size
        self.intervals = []
        self.id = nid
        self.typefreq = {}
        self.updateSize()
        self.competence = False

    def __str__(self):
        print("ID: ", self.id)
        print("Grid start: ", self.xmin)
        print("Grid end: ", self.xmax)
        print("Number of intervals: ", self.size)
        print("Current number of Intervals: ", self.currentsize)
        print("Type count: ", len(self.typefreq))
        if self.competence:
            print("Mace competence: ", self.competence)

        return ''

    def __getitem__(self, key):
        return self.intervals[key]

    def addInterval(self, interval):
        """Adds an Interval, adds an id and updates the Tier statistics"""
        self.intervals.append(interval)
        interval.id = len(self.intervals) - 1
        self.updateSize()
        if type(interval.text) == str:
            self.typefreq[interval.text] = self.typefreq.get(interval.text, 0) + 1

    def resize(self, newIntervals):
        """Updates Tier statistics if new Interval objects replace the existing
        Interval objects."""
        self.intervals = []
        for i in newIntervals:
            self.addInterval(i)
        self.size = len(self.intervals)

    def updateSize(self):
        """Updates the size of the Tier"""
        self.currentsize = len(self.intervals)
        try:
            assert self.currentsize <= self.size
        except AssertionError:
            print(self.currentsize)
            print(self.size)
            sys.exit('[', sys.arg[0] + ']: Size problem')

    def printGrid(self, filehandle):
        """Print function called by a TextGrid object to output a complete TextGrid
        Calls a similar functions on all Interval objects stored in the Tier."""

        header = ['class = "IntervalTier"',
                  'name = ' + self.id,
                  'xmin = ' + str(self.xmin),
                  'xmax = ' + str(self.xmax),
                  'intervals: size = ' + str(self.size)
                  ]

        filehandle.write('\n'.join([" " * 8 + x for x in header]) + '\n')

        for n, i in enumerate(self.intervals):
            filehandle.write(' ' * 8 + 'intervals [' + str(n + 1) + ']:\n')
            i.printGrid(filehandle)

    def timedInterval(self, start, end=False):
        """Returns the interval at the specified time. The time boundaries will
        rarely exactly match, so choose the minimum distance one. It is also
        possible to give a time frame and be returned a larger set of Interval
        objects."""

        assert type(start) == float
        interval1 = min(
            enumerate(self.intervals), key=lambda x: abs(x[1].xmin - start))

        if end:
            assert type(end) == float
            interval2 = self.timedInterval(end)
        else:
            interval2 = interval1

        return (interval1[0], interval2[0] + 1)

    def timedAnnotation(self, time):
        """Returns the annotation at of a tier at that time"""

        assert type(time) == float
        tgtInterval = min(
            enumerate(self.intervals), key=lambda x: abs(x[1].xmin - time))

        return tgtInterval.text

    def thresholdInterval(self, threshold, interval):
        """Compares an Interval object with numeric annotation with a
        threshold"""
        assert type(threshold) == float

        try:
            return float(interval.text.strip('"')) > threshold
        except:
            sys.exit("thresholdInterval(): Unable to compare " +
                     interval.text + " and " + str(threshold))


    def splitText(self, newTiername, glueleft, glueright):
        newIntervals = []
        for i in self.intervals:
            if i.text.strip() == '""' or i.viewable == False:
                # if viewable is False, i.text likely contains a list or array
                newIntervals.append(i.copy())
                continue
            letters = [x for x in i.text[1:-1]]
            newtext = []
            try:
                first = letters.pop(0)
            except IndexError:
                # Some thing in the formatting of the annotation is wrong
                newIntervals.append(i.copy(replace='""'))
                continue

            if first in glueright:
                first = first + letters.pop(0)
            mente = ''
            for l in letters:
                if mente != '':
                    # prefix current letter
                    first = mente + l
                    mente = ''
                elif l in glueleft:
                    # Append to first
                    first += l
                elif l in glueright:
                    # If $l is a prefix
                    mente = l
                    newtext.append(first)
                    first = l
                else:
                    # Base case
                    newtext.append(first)
                    first = l
            newtext.append(first)
            intervalDuration = i.xmax - i.xmin
            if len(newtext) <= 1:
                newIntervals.append(i.copy(replace='"' + newtext[0] + '"'))
                continue
            else:
                halfPhoneCount = len(newtext) * 2 + letters.count(
                    ':') + letters.count('ː')
                halfPhoneDuration = intervalDuration / halfPhoneCount

            xmin = i.xmin
            for phone in newtext:
                xmax = xmin + halfPhoneDuration * 2
                if ':' in phone or 'ː' in phone:
                    xmax += halfPhoneDuration
                newIntervals.append(Interval(xmin, xmax, '"' + phone + '"'))
                xmin = xmax

        return newIntervals
