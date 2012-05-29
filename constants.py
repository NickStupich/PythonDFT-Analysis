
#windowPolyFitSubtraction = False
windowPolyFitSubtraction = 5
	

baseFilename = "Data/Mark/32kSPS_160kS_FlexorRadialis_%d%%.xls"
#baseFilename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_%d%%.xls"

lowPercent = 0
highPercent = 10
transformsPerSecond = 30
type = 1

if type == 1:
	windowSize = 128
	samplesPerSecond = 768
	bins = [4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28]
elif type == 2:
	windowSize = 256
	samplesPerSecond = 1024
	bins = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
elif type == 3:
	windowSize = 128
	samplesPerSecond = 1024
	bins = [2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]
elif type == 4:
	windowSize = 167
	samplesPerSecond = 1000
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]
elif type == 5:
	windowSize = 111
	samplesPerSecond = 2000.0 / 3
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]	
elif type == 6:
	windowSize = 111
	samplesPerSecond = 1000.0/3
	bins = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]	
elif type == 7:
	windowSize = 222
	samplesPerSecond = 4000.0 / 3
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]	
elif type == 8:
	windowSize = 444
	samplesPerSecond = 8000.0/3
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]
elif type == 9:
	windowSize = 128
	samplesPerSecond = 808
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]
elif type == 10:
	windowSize = 500
	samplesPerSecond = 1000
	bins = range(6,28) + range(33, 58)
elif type == 11:
	windowSize = 250
	samplesPerSecond = 500
	bins = range(6,28, 2) + range(33, 58, 2	)
elif type == 12:
	windowSize = 111
	samplesPerSecond = 4000.0 / 3
	bins = [2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16]	
elif type == 13:
	windowSize = 1000
	samplesPerSecond = 10000
	bins = [2, 3, 4, 5, 7, 8, 9, 10, 11]
elif type == 14:
	windowSize = 222
	samplesPerSecond = 4000.0/3
	bins = [4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 25]	
else:
	raise Exception("invalid constants type")
	
#coherence of 60Hz noise.  1.0 = perfectly coherent, 0.0 = incoherent
coherence =2.0 * abs(0.5 - (60.0 * ((float(windowSize) / samplesPerSecond) % (1.0 / 60.0))))
resolution = (float(samplesPerSecond)/windowSize)


#print some info
print 'Base file: %s' % baseFilename
print 'Bins: %s' % str([int(bin * resolution) for bin in bins])
print "Window size: %d" % windowSize
print "Samples per second: %d" % samplesPerSecond
print "Transforms per second: %d" % transformsPerSecond
print "Frequency resolution: %fHz" % resolution
print "Coherence: %f" % coherence
print "Maximum frequency: %f" % (samplesPerSecond / 2)
print 'Window time length: %dms' % int(1000 * windowSize / samplesPerSecond)
print '60Hz cycles per window: %f' % (60.0 * windowSize / samplesPerSecond)