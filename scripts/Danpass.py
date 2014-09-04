import codecs
import os
import subprocess
from TextGrid import grid 
from praatparser import parse as gridParse

class DanPASS(object):
	"""docstring for DanPASS"""
	def __init__(self, corpuspath, outpath=False):
		super(DanPASS, self).__init__()
		self.corpuspath = corpuspath
		self.processedpath = outpath
		self.loadCorpus()

	def loadCorpus(self, path):

		assert os.path.exists(path) == True

		files = os.listdir(path)
		grids = [x for x in files if os.path.splitext(x)[1] == '.TextGrid']
		wavs = [x for x in files if os.path.splitext(x)[1] == '.wav']

		assert len(grids) == len(wavs)

		