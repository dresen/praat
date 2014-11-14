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
parser.add_option('-t', '--table',
                  dest="soundtype_tbl",
                  default=False,
                  action="store",
                  )
parser.add_option('-p', '--praatscript',
                  dest="psc",
                  default='f0-int-hnr_mono5ms.psc',
                  action="store",
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
monologues.globalDownsample16()
monologues.extractHnrTiers(options.psc)
monologues.extractPitchIntTiers(options.psc)
monologues.extractMfccTiers(options.psc)
monologues.splitAnnotation('"lydskrift"', '"segment"')
print(SCRIPT + "Annotations split", "...")
monologues.extractTiers('"segment"', '"stød-segment"', 'ˀ')
print(SCRIPT + "Tier extracted", "...")
monologues.MLdataFromTiers('"stød-segment"', write=True)
print(SCRIPT + "New ML data written to files", "...")

block = ['"POS"', '"POS (reduceret tagset)"', '"fonemnotation"',
         '"tryk og tone"', '"fraseintonation"', '"kommentarer"']

monologues.printGrids(filename=False, rmTiernames=block)
print(monologues)

# TODO:
#



