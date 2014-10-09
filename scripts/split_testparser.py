from Danpass import DanPASS
import os
import sys
import codecs
import optparse

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
parser.add_option('-c', '--corpus',
                  dest="fin",
                  default='../dp_mono/processed/',
                  )

options, remainder = parser.parse_args()

print(options)

try:
    assert os.path.isdir(options.fin) == True
except AssertionError:
    print("Unable to access directory.")
    sys.exit('Terminate.')

path = os.path.abspath(options.fin)
monologues = DanPASS(path, os.path.join(path, options.fout))

monologues.splitAnnotation('"lydskrift"', '"segment"')
print("Annotations split", "...")
monologues.extractTiers('"segment"', '"stød-segment"', 'ˀ')
print("Tier extracted", "...")
monologues.MLdataFromTiers('"stød-segment"', write=True)
print("New ML data written to files", "...")
block = []
monologues.printGrids(block)
print(monologues)

# TODO:
#


