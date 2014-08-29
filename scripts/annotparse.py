import os, sys, codecs
import optparse
import praatparser 


''' Read options from the command line
'''


parser = optparse.OptionParser()
parser.add_option('-o', '--output', 
                  dest="fout", 
                  default="new_enhanced.TextGrid",
                  )
parser.add_option('-t', '--table',
                  dest="soundtype_tbl",
                  default=False,
                  action="store",
                  )
parser.add_option('-i', '--input',
                  dest="fin",
                  default='alle_segment_praatipa_renset.TextGrid',
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
	print("Unable to access all necessary files." )
	sys.exit('Terminate.')




four = praatparser.parse(fin, os.path.abspath(options.fin), tbl)

segtiers = ['"IPA-1_segm"', '"IPA-2_segm"', '"IPA-3_segm"', '"IPA-4_segm"']

four.extractSegmentTier(segtiers, '"stødtier"', '\\^?')
four.extractSegmentTier(segtiers, '"maj"', '\\^?', 3)

print(four.getTier('"stødtier"'))

four.confusionMatrix(segtiers, 'zt.table')

four.mace(segtiers, 'zt.mace.csv', '/home/ask/software/MACE/MACE/MACE', 
                  '"Mace-prediction"')

for t in segtiers:
      print(four.getTier(t))

print(four.getTier('"Mace-prediction"'))

block = ['"IPA-1"', '"IPA-2"', '"IPA-3"', '"IPA-4"', '"PoS"',
            '"accent_word"', '"accent_syllable"', '"phone_type_cons_vow"' ]

four.printGrid(fout)
four.printGrid('zt', block)
