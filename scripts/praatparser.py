import os, sys, codecs
import optparse
from Interval import Interval
from Tier import Tier
from TextGrid import Grid



def parse(filepath, tbl=False):
	filehandle = codecs.open(filepath, 'r', 'utf8')
	## Parsing the TextGrid

	n = 0
	tierstart = False
	intervalstart = False
	for line in filehandle:
		elems = line.split()

		# Filter useless lines
		if len(elems) < 2:
			continue

		# Detect if a new tier starts
		if not tierstart and not intervalstart:  
			if elems[0] == 'class' and elems[-1] == '"IntervalTier"':
				tierstart = True

			# Else accumulate data for the Grid object
			elif elems[0] == 'xmin':
				grid_min = float(elems[-1])
			elif elems[0] == 'xmax':
				grid_max = float(elems[-1])
			elif elems[0] == 'size':
				grid_size = int(elems[-1])

				# Once grid size is found, create Grid object
				data = Grid(grid_min, grid_max, grid_size, 
					os.path.split(filepath)[-1])
			else:
				continue


		elif tierstart:
			if elems[0] == 'name':
				tiername = line.split('=')[-1].strip()
			elif elems[0] == 'xmin':
				tier_min = float(elems[-1])
			elif elems[0] == 'xmax':
				tier_max = float(elems[-1])
			elif elems[0] == 'intervals:' and elems[1] == 'size':
				tier_size = int(elems[-1])

				# Create empty Tier object
				tier = Tier(tier_min, tier_max, tier_size, tiername)
				data.addTier(tier)
				tierstart = False
				intervalstart = True

		elif intervalstart:
			if elems[0] == 'xmin':
				interval_min = float(elems[-1])
			elif elems[0] == 'xmax':
				interval_max = float(elems[-1])
			elif elems[0] == 'text':
				interval_text = line.split('=', 1)[-1].strip()

				tier.addInterval(Interval(interval_min, interval_max, interval_text.strip()))
			if elems[0] == 'item':
				intervalstart = False
				tierstart = True
	return data

