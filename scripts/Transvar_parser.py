from Danpass import DanPASS
import os
import sys
import codecs
import optparse

parser = optparse.OptionParser()
parser.add_option('-o', '--output',
                  dest="fout",
                  default="transvar_out",
                  )
parser.add_option('-t', '--table',
                  dest="soundtype_tbl",
                  default=False,
                  action="store",
                  )
parser.add_option('-c', '--corpus',
                  dest="fin",
                  default='../transvar/processed',
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
print(monologues)

monologues.globalDownsample16()
print("Downsampling done")
monologues.extractTiers('"Mace-prediction"', '"Mace-stød"', 'ˀ')
print("Tier extracted", "...")
monologues.extractHnrTiers('f0-int-hnr_mono.psc')
monologues.extractPitchIntTiers('f0-int-hnr_mono.psc')

annotations = ['"stødtier"', '"maj"', '"equal"', '"Mace-stød"', '"all"']

#for a in annotations:
  #monologues.setOutpath(a[1:-1])
monologues.MLdataFromTiers('"Mace-stød"', write=True, tbl_id="Mace-stød")
print("New ML data written to files", "...")

# The original outpath
#monologues.setOutpath(os.path.join(path, options.fout))
#block = []
#monologues.printGrids(block)
#print(monologues)

# TODO:
#


