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
                  default='../dp_mono',
                  )

options, remainder = parser.parse_args()

print(options)

try:
    assert os.path.isdir(options.fin) == True
except AssertionError:
    print("Unable to access directory.")
    sys.exit('Terminate.')

monologues = DanPASS(os.path.abspath(options.fin), )

monologues.extractTiers('"lydskrift"', '"stød-stavelse"', 'ˀ')
monologues.extractSegmentTiers(['"lydskrift"'], '"stød-kombineret"', 'ˀ')
monologues.globalDownsample16()
#monologues.extractHnrTiers('f0-int-hnr_mono.psc', downsample=16)
#monologues.pitchIntTiers('f0-int-hnr_mono.psc', options.sound, downsample=16)

print(monologues)

# data.extractTier('"lydskrift"', '"stød-stavelse"', 'ˀ')
# data.extractSegmentTier(['"lydskrift"'], '"stød-kombineret"', 'ˀ')
# #data.extractSegmentTier(['"lydskrift (ord-domæne)"'], '"stød-ord"', 'ˀ')

# block = ['"POS"', '"POS (reduceret tagset)"', '"fonemnotation"',
#          '"tryk og tone"', '"fraseintonation"', '"kommentarer"',
#          '"info-struktur"']

# data.hnrTier('f0-int-hnr_mono.psc', options.sound, downsample=16)
# #data.intensityTier('scripts/int-hnr_mono.psc', options.sound, downsample=16)
# data.pitchIntTier('f0-int-hnr_mono.psc', options.sound, downsample=16)

# # print(data)

# #print(data['"Pitch 1"'])
# data.prediction(data['"Harmonicity 2"'], '"stødpred"', '"ˀ"')
# data.printGrid(fout, block)

# TODO:
#


