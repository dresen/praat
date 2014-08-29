form input
    sentence stem
    sentence outputdir
endform

  	fileName$ = stem$ + ".wav"

#  	Read two Sounds from stereo file... 'fileName$'

#	noprogress To Pitch (ac)... 0.01 75 15 yes 0.03 0.45 0.01 0.4 0.14 600
#	Write to text file... 'outputdir$'/'stem$'_PtR.dat

#	Remove
  	Read two Sounds from stereo file... 'fileName$'
#	noprogress To Intensity... 75 0.005 yes
#	Write to text file... 'outputdir$'/'stem$'_INT.dat

	Remove
	select Sound 'stem$'_ch1
	Filter (pass Hann band)... 50 1000 100
	noprogress To Harmonicity (cc)... 0.005 50 0.1 1.0
	
	select Sound 'stem$'_ch1_band
	Remove
	select Harmonicity 'stem$'_ch1_band
	Write to text file... 'outputdir$'/'stem$'_HNR.dat