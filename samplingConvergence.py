import dataImport
from numpy.fft import rfft as fourier
from numpy import absolute
import plotting
from matplotlib import pylab
from math import log10, log, floor, ceil
import fftDataExtraction
import stats
#import constants
from noiseAnalysis import getToneLeakage

samplesPerSecond = 768
windowSize = 128
transformsPerSecond = 5

initialOffset = 1.0

filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls"; rawSps = 32000
class AdjacentBinsAdjustment:
	def __init__(self, sampleInterval):
		self.intervalChangeSize = sampleInterval * 0.001
		self.dir = 0
		self.lastDir = 0
		
	def OnNewBuffer(self, buffer, sampleInterval):
		freqData = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		#freqResolution = rawSps /( constants.windowSize * sampleInterval)
		freqResolution = samplesPerSecond / windowSize
		
		lowIndex = 60/freqResolution - 1
		highIndex = 60/freqResolution + 1
		
		lowMagnitude = freqData[9] + freqData[8] + freqData[7]
		highMagnitude = freqData[11] + freqData[12] + freqData[13]
		
		if lowMagnitude < highMagnitude:
			self.dir = 1
		elif lowMagnitude > highMagnitude:
			self.dir = -1
		else:
			self.dir = 0
		
		if self.dir * self.lastDir < 0:
			self.intervalChangeSize *= 0.9
		
		sampleInterval -= self.dir * self.intervalChangeSize
		self.lastDir = self.dir
		
		return sampleInterval
		
class AdjacentPowerAnnealing:
	def __init__(self, sampleInterval):
		self.intervalChangeSize = sampleInterval * 0.002
		self.lastLeakage = 999999.9
		self.lastInterval = sampleInterval
		
	def OnNewBuffer(self, buffer, sampleInterval):
		power = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		bins = [9, 11]
		leakage = sum([power[bin] for bin in bins])
		
		

def ConvergeOnCoherentSampling(rawData, rawSps):
	leakages = []
	sampleRates = []
	sampleInterval = rawSps / (samplesPerSecond + initialOffset)

	algorithm = AdjacentBinsAdjustment(sampleInterval)
	intervalCounter = 0.0
	
	bufferOverlap = windowSize / transformsPerSecond
	
	buffer = []
	
	lastSample = 0.0
	
	for sample in rawData:
		intervalCounter += 1.0
		if intervalCounter >= sampleInterval:
			intervalCounter %= sampleInterval
			weight0 = intervalCounter
			weight1 = 1.0 - intervalCounter
			
			interpolatedSample = weight0 * sample + weight1 * lastSample
			
			buffer.append(interpolatedSample)
			
			if len(buffer) == windowSize + bufferOverlap:
				buffer = buffer[bufferOverlap:]
				
				sampleInterval = algorithm.OnNewBuffer(buffer, sampleInterval)
				leakage = getToneLeakage(buffer)
				leakages.append(leakage)
				
				sampleRate = rawSps / sampleInterval
				sampleRates.append(sampleRate)
				
		lastSample = sample
	
	totalError = sum(leakages)
	print 'Total error through all time: %d' % totalError
	
	pylab.subplot(211)
	pylab.plot(range(len(sampleRates)), sampleRates)
	pylab.grid(True)
	pylab.subplot(212)
	pylab.plot(range(len(leakages)), leakages)
	pylab.grid(True)
	pylab.show()
	
if __name__ == "__main__":
	#data = dataImport.readADSFile(filename)
	data = dataImport.generateSignal(rawSps, [(60.0, 1.0)], seconds = 10.0)#, (120.0, 0.5), (180.0, 0.8)])
	
	ConvergeOnCoherentSampling(data, rawSps)
	