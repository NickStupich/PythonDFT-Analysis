import numpy
from numpy.fft import rfft as fourier
from matplotlib import pylab
from random import random, seed
import polyFitTest
import dataImport
import fftDataExtraction
import math
import stats

seed(1)

samplesPerSecond = 768
windowSize = 128
rangePercentage = 2.0
channels = 7
measurementCount = 10

filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls"; rawSps = 32000
#filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_0%.xls"; rawSps = 32000
rawData = dataImport.readADSFile(filename)
f = 59.96
#rawData = dataImport.generateSignal(rawSps, [(f, 1.0)], seconds = 5.0, noise = 1.0)

rawSps = 8000
rawData = fftDataExtraction.downSample(rawData, 32000, rawSps, interpolate = False)[int(random() * 100):]

overlap = 50 * 128 * rawSps / 768**2	#take this for all channels, could be slight different but ok

def getToneLeakage(downSampledData):
	noiseBin = 10
	power = map(lambda x: x*x, map(numpy.absolute, fourier(downSampledData)))
	result = (power[noiseBin-1] + power[noiseBin+1]) / power[noiseBin]
	#result = power[noiseBin-1] + power[noiseBin+1]
	return result
	
def GetConvergence(data, plot = True, initialOffset = 0.0):
	baseInterval = rawSps / (samplesPerSecond + initialOffset)
	
	channelIntervals = [baseInterval + rangePercentage * i * 0.02 for i in range(-channels/2+1, channels/2+1)]
	sampleFrequencies = map(lambda x: rawSps / x, channelIntervals)
	channelLeakages = [[] for _ in range(channels)]
	
	intervalCounters = [0.0] * channels
	
	buffers = [[] for _ in range(channels)]
	
	lastSample = 0.0
	startIndex = int(math.ceil(windowSize * max(channelIntervals)))
	for index, sample in enumerate(data):
		#add the sample to channels if necessary
		for c in range(channels):
			intervalCounters[c] += 1.0
			if intervalCounters[c] > channelIntervals[c]:
				intervalCounters[c] %= channelIntervals[c]
				weight0 = min(1.0, intervalCounters[c])
				weight1 = max(0.0, 1.0 - intervalCounters[c])
				interpolated = weight0 * sample + weight1 * lastSample
				buffers[c].append(interpolated)
				
		if index > startIndex and index % overlap == 0:
			for c in range(channels):
				leakage = getToneLeakage(buffers[c][-windowSize:])
				channelLeakages[c].append(leakage)
				
			if len(channelLeakages[0]) >= measurementCount:
				print 'total data collection time: %d ms' % (1000 * index / rawSps)
				break
		
		lastSample = sample
		
	means = []
	stdDevs = []
	
	for c in range(channels):
		means.append(stats.mean(channelLeakages[c]))
		stdDevs.append(stats.stdDev(channelLeakages[c]))
	errors = stdDevs
	
	for ys in zip(*channelLeakages):
		pylab.plot(sampleFrequencies, ys, 'bo')
		
	pylab.errorbar(sampleFrequencies, means, yerr=stdDevs, fmt='co')
	#print '\n'.join([str(x) for x in zip(sampleFrequencies, means, stdDevs)])
	
	#get the fit
	nextInterval, error = polyFitTest.polynomialFindMinimum(channelIntervals, means, errors = errors, order = 3, returnErrors = True)
	print nextInterval, error
	
	sps = rawSps / nextInterval
	sigma_sps = rawSps /(nextInterval**2.0) * error
	
	print 'Calculated samples per second: %f +/- %f' % (sps, sigma_sps)
	
	z = numpy.poly1d(polyFitTest.polynomialFit(sampleFrequencies, means, errors = errors, order = 3)[::-1])
	xp = numpy.linspace(min(sampleFrequencies)-2, max(sampleFrequencies)+2, 100)
	yp = z(xp)
	
	pylab.plot(xp, yp, 'g')
	#mins = [sps, sps-sigma_sps, sps+sigma_sps]
	pylab.errorbar(sps, z(sps), xerr=[sigma_sps], fmt='ro')
	
	
	pylab.grid(True)
	pylab.show()
	
if __name__ == "__main__":
	GetConvergence(rawData)