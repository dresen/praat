from praatparser import parse as gridParse
import os, sys, codecs
import optparse

parser = optparse.OptionParser()
parser.add_option('-o', '--output', 
                  dest="fout", 
                  default="new_enhanced.TextGrid",
                  )
parser.add_option('-s', '--sound',
                  dest="sound",
                  action="store",
                  default='Transvar_transuddrag.wav',
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

data = gridParse(fin, os.path.abspath(options.fin), tbl)

data.extractTier('"lydskrift"', '"stød-stavelse"', 'ˀ')
data.extractSegmentTier(['"lydskrift"'], '"stød-kombineret"', 'ˀ')
data.extractSegmentTier(['"lydskrift (ord-domæne)"'], '"stød-ord"', 'ˀ')

block = ['"POS"', '"POS (reduceret tagset)"', '"fonemnotation"', 
		'"tryk og tone"', '"fraseintonation"', '"kommentarer"',
		'"info-struktur"']

data.hnrTier('scripts/int-hnr_mono.psc', options.sound, downsample=16)
data.intensityTier('scripts/int-hnr_mono.psc', options.sound, downsample=16)

#print(data)

tierslice = data.timeSliceTier('"stød-stavelse"', 35, 36)

t = data['"stød-stavelse"']
for i in t[tierslice[0]:tierslice[1]]:
      print(i)

##TODO:
# fix the time slicing methods so they also work with two time indices


#data.printGrid(fout, block)


# class DanPASS(object):
# 	"""docstring for DanPASS"""
# 	def __init__(self, corpuspath, outpath=False):
# 		super(DanPASS, self).__init__()
# 		self.corpuspath = corpuspath
# 		self.processedpath = outpath
# 		self.mkPath(self.processedpath)
# 		self.loadCorpus()

# 	def mkPath

# 	def loadCorpus(self):
# 		"""Loads the corpus. Here the corpus has been preprocessed so the 
# 		TextGrids are in utf8 instead of utf16 or binary. The grids and wav 
# 		files are in the same directory too"""

# 		if self.processedpath:
# 			pass
# 		else:
# 			self.processedpath = self.mkPath(os.join(self.corpuspath, 'processed'))

# 		# We do not want to overwrite data
# 		assert os.path.exists(self.processedpath) == False
# 		os.mkdir(self.processedpath)



# 		grids = [x for x in os.listdir(corpuspath) if 'TextGrid' in x]

# 		for g in grids:
# 			gridParse(os.join(corpuspath, g), )
