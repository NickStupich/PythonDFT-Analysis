
type = 2

if type == 1:
	windowSize = 128
	samplesPerSecond = 768
	transformsPerSecond = 30
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]
elif type == 2:
	windowSize = 256
	samplesPerSecond = 1024
	transformsPerSecond = 30
	bins = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
elif type == 3:
	windowSize = 128
	samplesPerSecond = 1024
	transformsPerSecond = 30
	bins = [2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]
elif type == 4:
	windowSize = 167
	samplesPerSecond = 1000
	transformsPerSecond = 30
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]
elif type == 5:
	windowSize = 111
	samplesPerSecond = 2000.0/3
	transformsPerSecond = 30
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]	
elif type == 6:
	windowSize = 111
	samplesPerSecond = 1000.0/3
	transformsPerSecond = 30
	bins = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]	
elif type == 7:
	windowSize = 222
	samplesPerSecond = 4000.0 / 3
	transformsPerSecond = 30
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]	
elif type == 8:
	windowSize = 444
	samplesPerSecond = 8000.0/3
	transformsPerSecond = 30
	bins = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19]
	
	
else:
	raise Exception("invalid constants type")
	
#number of partial 60hz waves
coherence =2.0 * abs(0.5 - (60.0 * ((float(windowSize) / samplesPerSecond) % (1.0 / 60.0))))
	
#print some info
print "Window size: %d" % windowSize
print "Samples per second: %d" % samplesPerSecond
print "Transforms per second: %d" % transformsPerSecond
print "Frequency resolution: %fHz" % (float(samplesPerSecond)/windowSize)
print "Coherence: %f" % coherence
print "Maximum frequency: %f" % (samplesPerSecond / 2)
print 'Window time length: %dms' % int(1000 * windowSize / samplesPerSecond)