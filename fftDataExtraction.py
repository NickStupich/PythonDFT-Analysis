import dataImport
import re
from constants import *
from numpy.fft import rfft as fourier
from numpy import absolute
import plotting
from math import log10

def _downSample(rawData, rawSps):
	result = []
	for i in range(int(len(rawData) * samplesPerSecond / rawSps)):
		result.append(rawData[int(round(i * rawSps / samplesPerSecond))])
		
	return result
	
def getDownSampledData(filename):
	rawData = dataImport.readADSFile(filename)
	rawSps = dataImport.getSPS(filename)
	
	result = _downSample(rawData, rawSps)
	return result
	
def getFFTWindows(timeData):
	result = []
	windowOffset = int(samplesPerSecond / transformsPerSecond)
	for i in range(0, int(len(timeData) - windowSize), windowOffset):
		result.append(timeData[i:i+windowSize])
	#	print i, i+windowSize
		
	return result

def applyTransformsToWindows(windows, magnitude = False):
	frequencyDomains = map(fourier, windows)
	if magnitude:
		frequencyDomains = map(absolute, frequencyDomains)
		
	return frequencyDomains
	
def DoFrequencyBinning(frequencyDomains, logOfBin = False):
	return map(lambda x: [log10(x[bin]) if logOfBin else x[bin] for bin in bins], frequencyDomains)
	
def extractFFTData(filename, magnitude = False, applyBinning = False):
	downSampled = getDownSampledData(filename)	
	windows = getFFTWindows(downSampled)
	frequencyDomains = applyTransformsToWindows(windows, magnitude)
	
	if applyBinning:
		frequencyDomains = DoFrequencyBinning(frequencyDomains)
	
	return frequencyDomains, (float(samplesPerSecond) / windowSize)
	
	
if __name__ == "__main__":
	#filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_Transition%.xls"
	filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_0%.xls"
	frequencyDomains, binSpacing = extractFFTData(filename)
	
	#plotting.plotFrequencyDomain(frequencyDomains[0:-1:10], binSpacing, semilogY = True)
	
	filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_Transitions.xls"
	#filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_Transitions.xls"
	data = getDownSampledData(filename)
	plotting.plotSpectrogram(data)