class Tier(object):
	"""docstring for Tier"""
	def __init__(self, xmin, xmax, size, nid):
		super(Tier, self).__init__()
		self.xmin = xmin
		self.xmax = xmax
		self.size = size
		self.intervals = []
		self.id = nid
		self.typefreq = {}
		self.updateSize()
		self.competence = False

	def __str__(self):
		print("ID: ", self.id)
		print("Grid start: ", self.xmin)
		print("Grid end: ", self.xmax)
		print("Number of intervals: ", self.size)
		print("Current number of Intervals: ", self.currentsize)
		print("Type count: ", len(self.typefreq))
		if self.competence:
			print("Mace competence: ", self.competence)

		return ''

	def __getitem__(self, key):
		return self.intervals[key]

	def addInterval(self, interval):
		self.intervals.append(interval)
		interval.id = len(self.intervals)-1
		self.updateSize()
		self.typefreq[interval.text] = self.typefreq.get(interval.text, 0) + 1


	def resize(self, newIntervals):
		self.intervals = []
		for i in newIntervals:
			self.addInterval(i)
		self.size = len(self.intervals)

	def updateSize(self):
		self.currentsize = len(self.intervals)
		assert self.currentsize <= self.size

	def printGrid(self, filehandle):

		header = ['class = "IntervalTier"',
					'name = ' + self.id,
					'xmin = ' + str(self.xmin),
					'xmax = ' + str(self.xmax),
					'intervals: size = ' + str(self.size)					
					]	

		filehandle.write('\n'.join([" "*8 + x for x in header]) + '\n')

		for n, i in enumerate(self.intervals):
			filehandle.write(' '*8 + 'intervals [' + str(n+1) + ']:\n')
			i.printGrid(filehandle)

	def timedInterval(self, start, end=False):
		"""Returns the interval at the specified time. The time boundaries will
		rarely exectly match, so choose the minimum distance one. It is also 
		possible to give a time frame and be returned a larger set of Interval 
		objects."""
		
		assert type(start) == float
		interval1 = min(enumerate(self.intervals), key=lambda x: abs(x[1].xmin-start))

		if end:
			assert type(end) == float
			interval2 = self.timedInterval(end)
		else:
			interval2 = interval1

		return (interval1[0], interval2[0]+1)

	def thresholdInterval(self, threshold, interval):

		assert type(threshold) == float

		try:
			return float(interval.text) > threshold
		except:
			sys.exit("thresholdInterval(): Unable to compare " + interval.text + " and " + str(threshold))
		



