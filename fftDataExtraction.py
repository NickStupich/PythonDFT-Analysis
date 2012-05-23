from dataImport import readADSFile
import re
from constants import *
from numpy.fft import rfft as fourier
from numpy import absolute
import plotting

def _downSample(rawData, rawSps):
	result = []
	for i in range(int(len(rawData) * samplesPerSecond / rawSps)):
		result.append(rawData[int(round(i * rawSps / samplesPerSecond))])
		
	return result
	
def getDownSampledData(filename):
	rawData = readADSFile(filename)
	rawSps = int(filename.split('kSPS')[0].split('/')[-1]) * 1000
	
	result = _downSample(rawData, rawSps)
	return result
	
def getFFTWindows(timeData):
	result = []
	windowOffset = int(samplesPerSecond / transformsPerSecond)
	for i in range(0, int(len(timeData) - windowSize), windowOffset):
		result.append(timeData[i:i+windowSize])
	#	print i, i+windowSize
		
	return result

def extractFFTData(filename, magnitude = False):
	downSampled = getDownSampledData(filename)	
	windows = getFFTWindows(downSampled)
	frequencyDomains = map(fourier, windows)
	if magnitude:
		frequencyDomains = map(absolute, frequencyDomains)
	return frequencyDomains, (float(samplesPerSecond) / windowSize)
	
	
if __name__ == "__main__":
	filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls"
	#filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_100%.xls"
	frequencyDomains, binSpacing = extractFFTData(filename)
	
	plotting.plotFrequencyDomain(frequencyDomains[0:-1:10], binSpacing, semilogY = True)
	
	#filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_Transitions.xls"
	#filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_Transitions.xls"
	#data = getDownSampledData(filename)
	#plotting.plotSpectrogram(data)