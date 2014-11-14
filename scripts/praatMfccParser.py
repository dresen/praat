from Tier import Tier
from Interval import Interval
import numpy as np
import sys


def parse(filehandle):

	intervalstart = False
	dimno = 0
	for line in filehandle:
		elems = [x.strip() for x in line.split('=')]
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

			elif elems[0] == 'maximumNumberOfCoefficients':
				dimensions = float(elems[1]) + 1
				intervalstart = True
				
				# Increase size to hold first Interval object as padding
				mfccTier = Tier(xmin, xmax, size+1, objectclass)
				mfccTier.shift = shift
				text = np.zeros(dimensions) 
				first = Interval(0.0, start, text)
				mfccTier.addInterval(first)

			continue
		elif intervalstart:					

			if elems[0] == 'c0':
				dimno = 0
				vec = np.zeros(dimensions)
				vec[dimno] = float(elems[1])

			elif elems[0] == 'numberOfCoefficients':
				assert int(elems[1]) <= dimensions

			elif elems[0][0] == 'c':
				dimno += 1
				#print(dimno)
				vec[dimno] = float(elems[1])
				#print(vec)
				if dimensions == dimno+1:
					#print('here, ...')
					begin = mfccTier[-1].xmax
					end = begin + mfccTier.shift
					interval = Interval(begin, end, vec)
					interval.viewable = False
					mfccTier.addInterval(interval)

	return mfccTier


if __name__ == "__main__":
    # execute only if run as a script
    print(parse(open('../dp_mono/mfcc_out/m_009_h_16k_MFCC.dat')))