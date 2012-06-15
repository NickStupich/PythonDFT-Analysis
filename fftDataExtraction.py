import dataImport
import re
from constants import *
from numpy.fft import rfft as fourier
from numpy import absolute, polyfit
import plotting
from math import log10, floor, ceil
from matplotlib import pylab

def _downSample(rawData, rawSps, sps = samplesPerSecond):
	result = []
	for i in range(int(len(rawData) * sps / rawSps)):
		result.append(rawData[int(round(i * rawSps / sps))])
		
	return result
	
def _downSampleLinearInterpolate(rawData, rawSps, sps = samplesPerSecond):
	result = []
	sampleRatio = float(rawSps) / float(sps)
	for i in range(int(len(rawData) * sps / rawSps)):
		rawIndex = i * sampleRatio
		index0 = floor(rawIndex)
		index1 = ceil(rawIndex)
		if index0 == index1:
			val = rawData[int(index0)]
		else:
			val = (index1-rawIndex) * rawData[int(index0)] + (rawIndex-index0) * rawData[int(index1)]
		result.append(val)

	return result	
	
def downSample(rawData, rawSps, sps = samplesPerSecond, interpolate = True):
	if interpolate:
		return _downSampleLinearInterpolate(rawData, rawSps, sps)
	else:
		return _downSample(rawData, rawSps, sps)
	
def getDownSampledData(filename):
	rawData = dataImport.readADSFile(filename)
	rawSps = dataImport.getSPS(filename)
	
	result = downSample(rawData, rawSps)
	return result
	
def getFFTWindows(timeData):
	result = []
	windowOffset = int(samplesPerSecond / transformsPerSecond)
	for i in range(0, int(len(timeData) - windowSize), windowOffset):
		result.append(timeData[i:i+windowSize])
	#	print i, i+windowSize
		
	return result

def subtractPolynomialFit(window, degree):
	times = [float(x) for x in range(len(window))] #not actual times, but it doesn't matter
	coefficients = polyfit(times, window, degree)
	#print coefficients
	result = []
	for time, value in zip(times, window):
		fitValue = 0
		for power, c in enumerate(coefficients):
			fitValue += float(c)* (time ** float(len(coefficients)-1 - power))
		#print fitValue
		result.append(value - fitValue)
		
	return result
	
def applyTransformsToWindows(windows, magnitude = False, polyFitSubtraction = windowPolyFitSubtraction):
	timeData = []
	if polyFitSubtraction:
		for window in windows:
			timeData.append(subtractPolynomialFit(window, polyFitSubtraction))
	else:
		timeData = windows[:]
	
	frequencyDomains = map(fourier, timeData)
	if magnitude:
		frequencyDomains = map(absolute, frequencyDomains)
		
	return frequencyDomains
	
def DoFrequencyBinning(frequencyDomains, logOfBin = False, combineIfPossible = True):
	result = map(lambda x: [log10(x[bin]) if logOfBin else x[bin] for bin in bins], frequencyDomains)
	if combineIfPossible and combinedBins:
		result2 = map(lambda x: [(sum([x[cb] for cb in cbs])) for cbs in combinedBins], result)			
		return result2
		
	return result
	
	
def extractFFTData(filename, magnitude = False, applyBinning = False):
	downSampled = getDownSampledData(filename)	
	windows = getFFTWindows(downSampled)
	frequencyDomains = applyTransformsToWindows(windows, magnitude)
	
	if applyBinning:
		frequencyDomains = DoFrequencyBinning(frequencyDomains)
	
	return frequencyDomains, (float(samplesPerSecond) / windowSize)
	
def testPlotFrequencyDomain():
	filename = baseFilename % 0
	
	rawData = dataImport.readADSFile(filename)
	rawSps = 32000
	downSampled = _downSample(rawData, rawSps)
	downSampledLinear = _downSampleLinearInterpolate(rawData, rawSps)
	rawTimes = range(len(rawData))
	times = [float(x) * rawSps / samplesPerSecond for x in range(len(downSampled))]
	
	#pylab.plot(times, downSampled)
	#pylab.plot(rawTimes, rawData)
	#pylab.plot(times, downSampledLinear)
	pylab.show()
	
	index = 0
	fdat = applyTransformsToWindows(getFFTWindows(downSampled), True)[index]
	fdatLin = applyTransformsToWindows(getFFTWindows(downSampledLinear), True)[index]
	#print [str(x) for x in zip(fdat, fdatLin)]
	
	frequencies = [i * samplesPerSecond / windowSize for i in range(len(fdat))]
	
	pylab.semilogy(frequencies, fdat)
	pylab.semilogy(frequencies, fdatLin)
	pylab.grid(True)
	pylab.show()
	
if __name__ == "__main__":

	#testPlotFrequencyDomain()
	
	#filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_Transition%.xls"
	#filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_0%.xls"
	frequencyDomains, binSpacing = extractFFTData(baseFilename % 0)
	
	plotting.plotFrequencyDomain(frequencyDomains[0:-1:10], binSpacing, semilogY = False)
	
	#filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_Transitions.xls"
	#filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_Transitions.xls"
	#data = getDownSampledData(filename)
	#plotting.plotSpectrogram(data)