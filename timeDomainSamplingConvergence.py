import dataImport
import fftDataExtraction
import stats
from matplotlib import pylab

filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls"; rawSps = 32000
#filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_10%.xls"; rawSps = 32000
#filename = "NoiseData/6 Loops 8000SPS Volts.xls"; rawSps = 8000
rawData = dataImport.readADSFile(filename)
f = 60.0
#rawData = dataImport.generateSignal(rawSps, [(f, 1.0), (3.0 * f, 0.333)], seconds = 10.0)
rawData = fftDataExtraction.downSample(rawData, 32000, 8000, interpolate = False)

rawSps = 8000

#finalSps = 120.0
#downSampled = fftDataExtraction.downSample(rawData, rawSps, finalSps, interpolate = True)

def getSignalCoherenceError(downSampledFrequency, rawData = rawData):
	downSampled = fftDataExtraction.downSample(rawData, rawSps, downSampledFrequency, interpolate = True)
	#downSampled = downSampled[:int(downSampledFrequency)]
	highSamples = downSampled[::2]
	lowSamples = downSampled[1::2]

	times = map(lambda x: x/downSampledFrequency, range(len(downSampled)))
	highTimes = times[::2]
	lowTimes = times[1::2]
	
	differences = map(lambda x: (x[0]-x[1])**1.0, zip(highSamples, lowSamples))
	
	slope, yint = stats.lineOfBestFit(highTimes, differences)
	#return slope
	#return abs(slope)
	#return 1.0 / slope
	#return max(differences) - min(differences)
	
	return stats.variance(differences)
	
	
if __name__ == "__main__":
	if 1:
		frequencies = [f/1000.0 for f in range(119500, 120500, 1)]
		errors = map(getSignalCoherenceError, frequencies)
		
		pylab.plot(frequencies, errors)
		pylab.grid(True)
		pylab.show()
		
	else:
		for downSampledFrequency in [119.9, 119.95, 120.0, 120.05, 120.1]:
			#downSampledFrequency = 119.9
			downSampled = fftDataExtraction.downSample(rawData, rawSps, downSampledFrequency, interpolate = True)
			highSamples = downSampled[::2]
			lowSamples = downSampled[1::2]

			times = map(lambda x: x/downSampledFrequency, range(len(downSampled)))
			highTimes = times[::2]
			lowTimes = times[1::2]
			
			differences = map(lambda x: x[0]-x[1], zip(highSamples, lowSamples))
			diffTimes = highTimes[:len(differences)]
		
		#pylab.plot(times, downSampled, '-o')
		#pylab.plot(highTimes, highSamples, '-o')
		#pylab.plot(lowTimes, lowSamples, '-o')
		
			pylab.plot(diffTimes, differences)
			
		pylab.grid(True)
		pylab.show()
	