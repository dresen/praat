from Danpass import DanPASS
import os
import sys
import codecs
import optparse

SCRIPT = '[Transvar_extend.py]: '

parser = optparse.OptionParser()
parser.add_option('-o', '--output',
                  dest="fout",
                  default="transvar_extended",
                  )
parser.add_option('-t', '--tables',
                  dest="tables",
                  default='../5ms/predictions',
                  action="store",
                  )
parser.add_option('-c', '--corpus',
                  dest="fin",
                  default='../transvar/processed/',
                  )

options, remainder = parser.parse_args()

try:
    assert os.path.isdir(options.fin) == True
    assert os.path.isdir(options.tables) == True
except AssertionError:
    print(SCRIPT, "Unable to access directory.")
    sys.exit('Terminate.')

path = os.path.abspath(options.fin)
transvar = DanPASS(path, os.path.join(path, options.fout))
print(SCRIPT, transvar)

ml_annotations = os.listdir(options.tables)
gridname = 'Transvar_transuddrag.TextGrid'
used_ml_annotations = []
for a in ml_annotations:
    tbl_loc = os.path.join(options.tables, a)
    tier_id = a.split('.', 1)[0]
    tiernameSample = '"' + tier_id + 'sample"'
    tiername = '"' + tier_id + '"'
    transvar.addMLTier(gridname, tiernameSample, tbl_loc)
    transvar[gridname].extractSegmentTier([tiernameSample], tiername, '\\^?')
    newgrid = tier_id + '.TextGrid'
    used_ml_annotations.append(tiernameSample)
    transvar.printGrids(filename=newgrid, rmTiernames=used_ml_annotations)
    used_ml_annotations.append(tiername)

