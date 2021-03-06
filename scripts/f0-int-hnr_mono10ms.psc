form input
	sentence path
    sentence stem
    sentence outputdir
endform

  	fileName$ = stem$ + ".wav"

  	Read from file... 'path$'/'fileName$'
	Filter (pass Hann band)... 50 1000 100
	select Sound 'stem$'
	Remove
	select Sound 'stem$'_band
	noprogress To Pitch (ac)... 0.01 75 15 yes 0.03 0.45 0.01 0.4 0.14 600
	Write to text file... 'outputdir$'/'stem$'_PtR.dat
	select Pitch 'stem$'_band
	Remove

	select Sound 'stem$'_band
	noprogress To Harmonicity (cc)... 0.01 50 0.1 1.0
	select Harmonicity 'stem$'_band
	Write to text file... 'outputdir$'/'stem$'_HNR.dat