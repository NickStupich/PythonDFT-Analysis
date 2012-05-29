import dataImport
from numpy.fft import rfft as fourier
from numpy import absolute
import plotting
from matplotlib import pylab
from math import log10, log, floor, ceil, exp, sqrt
import fftDataExtraction
import stats
from random import random
#import constants
from noiseAnalysis import getToneLeakage

samplesPerSecond = 768
windowSize = 128
transformsPerSecond = int(samplesPerSecond / windowSize)

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
		
		return sampleInterval, sampleInterval
		
class AdjacentPowerAnnealing:
	def __init__(self, sampleInterval):
		self.intervalChangeSize = sampleInterval * 0.001
		self.lastLeakage = 999999.9
		self.lastInterval = sampleInterval
		
		self.bestInterval = self.lastInterval
		self.bestLeakage = self.lastLeakage
		
		self.t = 10
		
	def __CanMoveUphill(self):
		result = random() < 0.1 + 0.5 * exp(-1.0 * self.t)
		return result
		
	def OnNewBuffer(self, buffer, sampleInterval):
		self.t += 1
		power = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		bins = [9, 11]
		leakage = sum([power[bin] for bin in bins])
		
		if leakage > self.lastLeakage and not self.__CanMoveUphill():
			return self.lastInterval, self.bestInterval
		
		if leakage < self.bestLeakage:
			self.bestLeakage = leakage
			self.bestInterval = self.lastInterval
			
		#move in a random direction by a scaled random amount
		x = 20.0
		movement = (random() - 0.5) * self.intervalChangeSize * x / (self.t + x) 
		
		self.lastLeakage = leakage
		self.lastInterval = sampleInterval
		
		return (sampleInterval + movement), self.bestInterval
		
		
class RandomLeapKeepBest:
	def __init__(self, sampleInterval):
		self.bestInterval = sampleInterval
		self.bestLeakage = 999999999.9
		self.t = 10
		
	def OnNewBuffer(self, buffer, sampleInterval):
		self.t += 1
		power = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		bins = [8, 9, 11, 12]
		leakage = sum([power[bin] for bin in bins])
		
		if leakage < self.bestLeakage:
			self.bestLeakage = leakage
			self.bestInterval = sampleInterval
			print (rawSps / self.bestInterval), self.bestLeakage
			
		newInterval = self.bestInterval * (1.0 + 0.005 * (random() - 0.5)/sqrt(self.t))
		return newInterval, self.bestInterval

def ConvergeOnCoherentSampling(rawData, rawSps):
	leakages = []
	bestLeakages = []
	sampleRates = []
	bestRates = []
	sampleInterval = rawSps / (samplesPerSecond + initialOffset)

	#algorithm = AdjacentBinsAdjustment(sampleInterval)
	algorithm = AdjacentPowerAnnealing(sampleInterval)
	#algorithm = RandomLeapKeepBest(sampleInterval)
	
	intervalCounter = 0.0
	bestIntervalCounter = 0.0
	bufferOverlap = windowSize / transformsPerSecond
	
	buffer = []
	bestBuffer = []
	bestInterval = sampleInterval
	lastSample = 0.0
	
	for sample in rawData:
		intervalCounter += 1.0
		bestIntervalCounter += 1.0
		if bestIntervalCounter >= bestInterval:
			bestIntervalCounter %= bestInterval
			weight0 = bestIntervalCounter
			weight1 = 1.0 - bestIntervalCounter
			
			interpolatedSample = weight0 * sample + weight1 * lastSample
			bestBuffer.append(interpolatedSample)
			bestBuffer = bestBuffer[-windowSize:]
			
		if intervalCounter >= sampleInterval:
			intervalCounter %= sampleInterval
			weight0 = intervalCounter
			weight1 = 1.0 - intervalCounter
			
			interpolatedSample = weight0 * sample + weight1 * lastSample
			
			buffer.append(interpolatedSample)
			
			if len(buffer) == windowSize + bufferOverlap:
				buffer = buffer[bufferOverlap:]
				
				sampleInterval, bestInterval = algorithm.OnNewBuffer(buffer, sampleInterval)
				
				leakage = getToneLeakage(buffer)
				leakages.append(leakage)
				
				bestLeakage = getToneLeakage(bestBuffer)
				bestLeakages.append(bestLeakage)
				
				sampleRate = rawSps / sampleInterval
				sampleRates.append(sampleRate)
				
				bestRates.append(rawSps / bestInterval)
				
		lastSample = sample
	
	totalError = sum(leakages)
	print 'Total error through all time: %d' % totalError
	
	
	fig, ax = pylab.subplots()
	#pylab.subplot(211)
	ax.plot(range(len(sampleRates)), sampleRates, 'Blue')
	ax.plot(range(len(sampleRates)), bestRates, 'Red')
	ax.plot([0, 0], [767, 769])
	#pylab.grid(True); pylab.subplot(212)
	ax.twinx().plot(range(len(leakages)), leakages, color = 'Blue')
	ax.twinx().plot(range(len(bestLeakages)), leakages, color = 'Red')
	pylab.grid(True); pylab.show()
	
if __name__ == "__main__":
	#data = dataImport.readADSFile(filename)
	data = dataImport.generateSignal(rawSps, [(60.0, 1.0)], seconds = 10.0)#, (120.0, 0.5), (180.0, 0.8)])
	
	ConvergeOnCoherentSampling(data, rawSps)
	