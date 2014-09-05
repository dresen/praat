from praatparser import parse as gridParse
import os
import sys
import codecs
import optparse

parser = optparse.OptionParser()
parser.add_option('-o', '--output',
                  dest="fout",
                  default="../dp_mono/m_033_k.processed.TextGrid",
                  )
parser.add_option('-s', '--sound',
                  dest="sound",
                  action="store",
                  default='../dp_mono/m_033_k.wav',
                  )
parser.add_option('-t', '--table',
                  dest="soundtype_tbl",
                  default=False,
                  action="store",
                  )
parser.add_option('-i', '--input',
                  dest="fin",
                  default='../dp_mono/m_033_k.TextGrid',
                  )

options, remainder = parser.parse_args()

print(options)

try:
    fin = codecs.open(options.fin, 'r', 'utf8')
    fout = codecs.open(options.fout, 'w', 'utf8')
    if options.soundtype_tbl:
        tbl = codecs.open(options.soundtype_tbl, 'r', 'utf8')
    else:
        tbl = False
except:
    print("Unable to access all necessary files.")
    sys.exit('Terminate.')

data = gridParse(os.path.abspath(options.fin), tbl)

data.extractTier('"lydskrift"', '"stød-stavelse"', 'ˀ')
data.extractSegmentTier(['"lydskrift"'], '"stød-kombineret"', 'ˀ')
#data.extractSegmentTier(['"lydskrift (ord-domæne)"'], '"stød-ord"', 'ˀ')

block = ['"POS"', '"POS (reduceret tagset)"', '"fonemnotation"',
         '"tryk og tone"', '"fraseintonation"', '"kommentarer"',
         '"info-struktur"']

data.hnrTier('f0-int-hnr_mono.psc', options.sound, downsample=16)
#data.intensityTier('scripts/int-hnr_mono.psc', options.sound, downsample=16)
data.pitchIntTier('f0-int-hnr_mono.psc', options.sound, downsample=16)

# print(data)

#print(data['"Pitch 1"'])
data.prediction(data['"Harmonicity 2"'], '"stødpred"', '"ˀ"')
data.printGrid(fout, block)

# TODO:



