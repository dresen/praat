import sys


class Interval(object):

    """docstring for Interval
    Interval is the smallest class in the Praat parsing system. It contains
    the annotation and the time window, but not much else."""

    def __init__(self, xmin, xmax, text):
        super(Interval, self).__init__()
        self.xmin = xmin
        self.xmax = xmax
        self.text = text
        self.id = ""

    def __str__(self):
        """Print function"""
        print("ID: ", self.id)
        print("Interval start: ", self.xmin)
        print("Interval end: ", self.xmax)
        print("Annotation: ", self.text)

        return ''

    def printGrid(self, filehandle):
        """Print function called by a Tier object to output a complete TextGrid"""
        data = ['xmin = ' + str(self.xmin),
                'xmax = ' + str(self.xmax),
                'text = ' + self.text
                        ]
        filehandle.write('\n'.join([" " * 12 + x for x in data]) + '\n')

    def copy(self, replace=False):
        """Use to prevent pass-by-reference"""
        if replace:
            return Interval(self.xmin, self.xmax, replace)
        else:
            return Interval(self.xmin, self.xmax, self.text)

    def merge(self, other, replace=False, func=False):
        """Merges adjacent Interval objects in a tier"""
        if self.xmax == other.xmin:
            left, right = self, other
        elif other.xmax == self.xmin:
            left, right = other, self
        else:
            sys.exit('Interval.merge(): boundary times do not match.')
        if replace:
            newtext = replace
        elif func:
            newtext = func(left.text, right.text)
        else:
            newtext = " ".join((left.text, right.text))

        return Interval(left.xmin, right.xmax, newtext)
