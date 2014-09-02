from Tier import Tier
from Interval import Interval
from operator import itemgetter


def parse(filehandle):
    """Returns two tiers. One with Intensity measures and one with pitch
    candidates. The filehandle must reference a Praat Pitch object text
    file."""

    intervalstart = False
    candidatestart = False
    candidates = []
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

            elif elems[0] == 'ceiling':
                ceiling = int(elems[1])

            elif elems[0] == 'maxnCandidates':
                maxnCandidates = int(elems[1])

            elif elems[0] == 'intensity':
            	# Iteration never returns here because intervalstart is True
                intervalstart = True
                intTier = Tier(xmin, xmax, size, '"Intensity"')
                text = '"' + elems[1] + '"'

            	# Set begin and end so they can be used in the next iteration
            	# to set the first Interval for the pitch Tier
                begin = 0.0
                end = start
                intTier.addInterval(Interval(begin, end, text))
                pitchTier = Tier(xmin, xmax, size, objectclass)
                # Prepare candidate list for first Interval
                # First iteration skips the intensity condition below
                candidates.append((0, 0))

        elif intervalstart:

            if elems[0] == 'intensity':
                begin = intTier[-1].xmax
                end = begin + shift
                text = '"' + elems[1] + '"'
                intTier.addInterval(Interval(begin, end, text))
                candidates = []

            elif elems[0] == 'nCandidates':
                nc = int(elems[1])
                candidatestart = True

            elif candidatestart:

                if elems[0] == "frequency":
                    freq = float(elems[1])
                elif elems[0] == "strength":
                    strength = float(elems[1])
                    candidates.append((freq, strength))

                if len(candidates) == nc:
                	# Candidate are ranked according to a decoding algorithm
                	# First candidate is most likely, but we parse them all
                    pitchTier.addInterval(
                        Interval(begin, end, '"' + str(candidates[0][0]) + '"'))
                    candidatestart = False

    return (pitchTier, intTier)
