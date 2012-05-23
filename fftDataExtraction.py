from dataImport import readADSFile
import re
from constants import *
from numpy.fft import rfft as fourier
import plotting


def _downSample(rawData, rawSps):
	result = []
	for i in range(len(rawData) * samplesPerSecond / rawSps):
		result.append(rawData[i * rawSps / samplesPerSecond])
		
	return result
	
def getDownSampledData(filename):
	rawData = readADSFile(filename)
	rawSps = int(filename.split('kSPS')[0].split('/')[-1]) * 1000
	
	result = _downSample(rawData, rawSps)
	return result
	
def getFFTWindows(timeData):
	result = []
	windowOffset = samplesPerSecond / transformsPerSecond
	for i in range(0, len(timeData) - windowSize, windowOffset):
		result.append(timeData[i:i+windowSize])
	#	print i, i+windowSize
		
	return result

def extractFFTData(filename):
	downSampled = getDownSampledData(filename)	
	windows = getFFTWindows(downSampled)
	frequencyDomains = map(fourier, windows)
	return frequencyDomains, (float(samplesPerSecond) / windowSize)
	
	
	
if __name__ == "__main__":
	#frequencyDomains, binSpacing = extractFFTData("Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls")
	frequencyDomains, binSpacing = extractFFTData("Data/Mark/32kSPS_160kS_ExtensorRadialis_100%.xls")
	#print len(frequencyDomains)
	plotting.plotFrequencyDomain(frequencyDomains[0:-1:10], binSpacing, semilogY = True)