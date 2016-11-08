import os
import sys
import codecs
import optparse
from Danpass import DanPASS

SCRIPT = '[danpass_parser.py]: '

parser = optparse.OptionParser()
parser.add_option('-o', '--output',
                  dest="fout",
                  default="danpass_out",
                  )
parser.add_option('-c', '--corpus',
                  dest="fin",
                  default='../dp_mono/processed/test',
                  )

options, remainder = parser.parse_args()

try:
    assert os.path.isdir(options.fin) == True
except AssertionError:
    print("Unable to access directory.")
    sys.exit('Terminate.')
path = os.path.abspath(options.fin)
monologues = DanPASS(path, os.path.join(path, options.fout))
monologues.printKaldiData(os.path.join(path, 'danpass_kaldi'))


# TODO:
#
