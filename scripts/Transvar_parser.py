from Danpass import DanPASS
import os
import sys
import codecs
import optparse

SCRIPT = '[Transvar_parser.py]: '

parser = optparse.OptionParser()
parser.add_option('-o', '--output',
                  dest="fout",
                  default="transvar_out/ml",
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
                  default='../transvar/processed/',
                  )

options, remainder = parser.parse_args()

try:
    assert os.path.isdir(options.fin) == True
except AssertionError:
    print(SCRIPT, "Unable to access directory.")
    sys.exit('Terminate.')

path = os.path.abspath(options.fin)
transvar = DanPASS(path, os.path.join(path, options.fout))
print(SCRIPT, transvar)

transvar.globalDownsample16()
print(SCRIPT, "Downsampling done")
transvar.extractTiers('"Mace-prediction"', '"Mace-stød"', 'ˀ')
print(SCRIPT, "Tier extracted", "...")
transvar.extractHnrTiers(options.psc)
transvar.extractPitchIntTiers(options.psc)

annotations = ['"stødtier"', '"maj"', '"equal"', '"Mace-stød"', '"all"', '"Mace-prediction"']
for a in annotations:
  transvar.MLdataFromTiers(a, write=True, tbl_id=a)
print("New ML data written to files", "...")

#transvar.addMLTier('Transvar_transuddrag.TextGrid', '"NB"', '../predictions/NB.pred.tbl')

#transvar.printGrids()

