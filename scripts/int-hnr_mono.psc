form input
	sentence path
    sentence stem
    sentence outputdir
endform

  	fileName$ = stem$ + ".wav"

  	Read from file... 'path$'/'fileName$'
	noprogress To Intensity... 75 0.005 yes
	Write to text file... 'outputdir$'/'stem$'_INT.dat
	select Intensity 'stem$'
	Remove
	
	select Sound 'stem$'
	Filter (pass Hann band)... 50 1000 100
	noprogress To Harmonicity (cc)... 0.005 50 0.1 1.0
	
	select Sound 'stem$'
	Remove
	select Harmonicity 'stem$'_band
	Write to text file... 'outputdir$'/'stem$'_HNR.dat