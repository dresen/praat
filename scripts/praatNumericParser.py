from Tier import Tier
from Interval import Interval


def parse(filehandle):

	intervalstart = False
	for line in filehandle:
		elems = [x.strip() for x in line.split('=')]
		#print(elems[0])
		# Filter useless lines
		if len(elems) < 2:
			continue
		if not intervalstart:
			if elems[0] == 'Object class':
				objectclass = elems[1]
				
			elif elems[0] == 'xmin':
				xmin = float(elems[1])
				
			elif elems[0] == 'xmax':
				xmax = float(elems[1])
				
			elif elems[0] == 'nx':
				size = int(elems[1])
				
			elif elems[0] == 'dx':
				shift = float(elems[1])
				
			elif elems[0] == 'x1':
				start = float(elems[1])
				
			elif elems[0] == 'z [1] [1]':
				intervalstart = True
				
				
				hnrTier = Tier(xmin, xmax, size, objectclass)
				hnrTier.shift = shift
				text = '"' + elems[1] + '"'
				hnrTier.addInterval(Interval(0.0, start, text))

			continue
		elif intervalstart:
			begin = hnrTier[-1].xmax
			end = begin + hnrTier.shift
			text = '"' + elems[1] + '"'
			hnrTier.addInterval(Interval(begin, end, text))

	return hnrTier
