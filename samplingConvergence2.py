import dataImport
from numpy.fft import rfft as fourier
from numpy import absolute, polyfit
import plotting
import numpy
from matplotlib import pylab
from math import log10, log, floor, ceil, exp, sqrt, sin, pi
import fftDataExtraction
import stats
from random import random, seed
#import constants
#from __future__ import division
import sys
import functools
import polyFitTest
import functools

seed(1)

samplesPerSecond = 768
windowSize = 128
transformsPerSecond = 30
noiseBin = 20

#filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls"; rawSps = 32000
filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_0%.xls"; rawSps = 32000
#filename = "NoiseData/6 Loops 8000SPS Volts.xls"; rawSps = 8000
rawData = dataImport.readADSFile(filename)
f = 59.96
#rawData = dataImport.generateSignal(rawSps, [(f, 1.0), (2.0*f, 0.5)], seconds = 5.0)

fDown = 8000.0

rawSps = 8000.0; rawData = fftDataExtraction.downSample(rawData, 32000, fDown, interpolate = False)[int(random() * 100):]
#print 'Ideal sample rate: %s' % (59.96 / 60.0 * samplesPerSecond * rawSps / fDown)
rangePercentage = 2.0

def getToneLeakage(downSampledData):
	power = map(lambda x: x*x, map(absolute, fourier(downSampledData)))
	result = (power[noiseBin-1] + power[noiseBin+1]) / power[noiseBin]
	#result = power[noiseBin-1] + power[noiseBin+1]
	return result
	
class TestAlgorithm:
	def __init__(self, sampleInterval):
		pass
	def OnNewBuffer(self, buffer, sampleInterval):
		return sampleInterval, sampleInterval
		
class RandomLeapKeepBest:
	def __init__(self, sampleInterval, leapSize = 0.02, decayPow = 0.8):
		self.bestInterval = sampleInterval
		self.bestLeakage = 999999999.9
		self.t = 10
		self.leapSize = leapSize
		self.decayPow = decayPow
		self.lastInterval = sampleInterval
		
	def OnNewBuffer(self, buffer, sampleInterval):
		self.t += 1
		power = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		bins = [9, 11]
		leakage = sum([power[bin] for bin in bins])
		
		if leakage < self.bestLeakage:
			self.bestLeakage = leakage
			self.bestInterval = self.lastInterval
			
		#self.lastInterval = self.bestInterval * (1.0 + self.leapSize * (random() - 0.5)/(self.t**self.decayPow))
		#maxLeapSize = self.leapSize / log10(self.t)
		maxLeapSize = self.leapSize / (self.t**self.decayPow)
		
		self.lastInterval = self.bestInterval * (1.0 + maxLeapSize * (random() - 0.5))
		
		return self.bestInterval, self.lastInterval
		
class SimulatedAnnealing:
	def __init__(self, sampleInterval):
		self.bestInterval = sampleInterval
		self.bestLeakage = 9999999999.9
		
		self.lastLeakage = 9999999999.9
		self.lastInterval = sampleInterval
		
		self.t = 10
		
	def CanMoveUphill(self):
		result = random() < 0.1 + 0.5 * exp(-1.0 * self.t)
		
	def OnNewBuffer(self, buffer, sampleInterval):	
		self.t += 1
		
		power = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		bins = [9, 11]
		leakage = sum([power[bin] for bin in bins])
		
		if self.lastInterval == sampleInterval:
			#print 'passing...'
			pass
		elif leakage < self.lastLeakage:
			if leakage < self.bestLeakage:
				self.bestLeakage = leakage
				self.bestInterval = sampleInterval
			
			self.lastLeakage = leakage
			self.lastInterval = sampleInterval
			
		else:
			if self.CanMoveUphill():
				self.lastLeakage = leakage
				self.lastInterval = sampleInterval
			else:
				#print 'here'
				return self.bestInterval, self.lastInterval
		
		#make a random guess in some direction
		newInterval = self.lastInterval * (1.0 + 0.01 * (random() - 0.5)/(self.t**0.8))
		
		return self.bestInterval, newInterval

class ShapeMatching:
	def __init__(self, sampleInterval, increment = 0.01):
		self.shapes = []
		increment = 0.01; bottom = 764.0; top = 772.0
		
		frequencies = range(0, 384+1, 6)
		
		for sps in [bottom + increment * i for i in range(int((top-bottom)/increment))]:
			timeData = [sin(60.0*2.0 * pi * t/sps) for t in range(windowSize)]
			freqData = self.normalize(map(absolute, fourier(timeData)))
			
			self.shapes.append((sps, freqData))
		
	def normalize(self, freqData):
		s = sum(freqData)
		result = [f/s for f in freqData]
		return result
		
	def distance(self, data1, data2):
		return sum([(x1-x2)**2 for x1, x2 in zip(data1, data2)])
		
	def OnNewBuffer(self, buffer, sampleInterval):
		fData = self.normalize(map(absolute, fourier(buffer)))
		
		closest = None
		for sps, data in self.shapes:
			dist = self.distance(data, fData)
			if closest is None or dist < closest[0]:
				closest = (dist, sps)
				
		newSampleInterval = sampleInterval * closest[1] / samplesPerSecond
		
		print closest, (rawSps / newSampleInterval), (rawSps / sampleInterval)
		return newSampleInterval, newSampleInterval
		
class HybridShapeRandom:
	def __init__(self, sampleInterval):
		self.FirstLoop = True
		self.shapeMatch = ShapeMatching(sampleInterval, increment = 0.1)
		self.randomLeap = RandomLeapKeepBest(sampleInterval, leapSize = 0.004, decayPow = 1.0)
		
	def OnNewBuffer(self, buffer, sampleInterval):
		if self.FirstLoop:
			self.FirstLoop = False
			return self.shapeMatch.OnNewBuffer(buffer, sampleInterval)
		else:
			return self.randomLeap.OnNewBuffer(buffer, sampleInterval)
		
class PeakImbalance:
	def __init__(self, sampleInterval, leapSize = 0.01, decayPow = 1.0):
		self.bestInterval = sampleInterval
		self.bestLeakage = 999999999.9
		self.t = 10
		self.leapSize = leapSize
		self.decayPow = decayPow
		
	def OnNewBuffer(self, buffer, sampleInterval):
		power = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		
		leakage = power[9] + power[11]
		
		if leakage < self.bestLeakage:
			self.bestLeakage = leakage
			self.bestInterval = sampleInterval
			
		left = power[8] + power[9]
		right = power[11] + power[12]
		center = (left) / (left + right) - 0.5
		#print left, right, center, rawSps / sampleInterval
		newInterval = self.bestInterval * (1.0 + self.leapSize * (random() - center) / (self.t**self.decayPow))
			
		return self.bestInterval, newInterval
		
class QuadraticErrorFitting:
	def __init__(self, sampleInterval, initialLeapSize = 0.04):
		self.bestInterval = sampleInterval
		self.bestLeakage = 999999999.9
		self.initialLeapSize = initialLeapSize
		
		self.xs = []
		self.ys = []
		
	def OnNewBuffer(self, buffer, sampleInterval):
		power = map(lambda x: absolute(x) ** 2.0, fourier(buffer))
		
		leakage = power[9] + power[11]
		
		if leakage < self.bestLeakage:
			self.bestLeakage = leakage
			self.bestInterval = sampleInterval
		
		self.xs.append(sampleInterval)
		self.ys.append(leakage)
		
		if len(self.xs) > 5:
			#fit quadratic to the leakages and sample intervals
			coefficients = polyfit(self.xs, self.ys, 2)
			nextInterval = stats.quadraticMinimum(*coefficients)
			
			self.bestInterval = nextInterval
			#print rawSps / nextInterval
			
		else:
			nextInterval = self.bestInterval * (1.0 + self.initialLeapSize*(random() - 0.5))
			
		print rawSps / nextInterval
			
		return self.bestInterval, nextInterval
		
class QuadraticErrorFitting2:
	def __init__(self, sampleInterval):
		low = samplesPerSecond * (1.0 - rangePercentage / 100)
		high = samplesPerSecond *(1.0 + rangePercentage / 100)
		steps = 6
		self.startingXs = [float(fDown) / x for x in [low + i * (high-low)/steps for i in range(steps)]]
		self.xs = []
		self.ys = []
		self.coefficients = None
		
	def GetFirstInterval(self):
		return self.startingXs.pop()
		
	def OnNewBuffer(self, buffer, sampleInterval, returnIsDone = False):
		leakage = getToneLeakage(buffer)

		self.xs.append(sampleInterval)
		self.ys.append(leakage)
		
		if self.startingXs:
			nextInterval = self.startingXs.pop()
		elif self.coefficients is None:
			"""
			fit = polyfit(self.xs, self.ys, 2, full=True)
			print fit
			self.coefficients = fit[0]
			
			#p = numpy.poly1d(self.coefficients)
			#pylab.plot(self.xs, self.ys, self.xs, p(self.xs)); pylab.show()
			
			nextInterval = stats.quadraticMinimum(*self.coefficients)
			"""
			self.coefficients = 1
			#errors = [1.0] * len(self.xs)
			errors = [sqrt(y) for y in self.ys]
			nextInterval, error = polyFitTest.polynomialFindMinimum(self.xs, self.ys, errors = errors, order = 3, returnErrors = True)
			#print nextInterval, error
			sps = rawSps / nextInterval
			sigma_sps = rawSps /(nextInterval**2.0) * error
			#print 'sps: %f +/- %f' % (sps, sigma_sps)
			
			if returnIsDone:
				return nextInterval, nextInterval, True
				
		else:
			if returnIsDone:
				return sampleInterval, sampleInterval, True
			else:
				return sampleInterval, sampleInterval
		
		if returnIsDone:
			return nextInterval, nextInterval, False
		else:
			return nextInterval, nextInterval
		
class GoertzelValues:
	def __init__(self, sampleInterval):
		self.frequencies = [x / 10.0 for x in range(590, 610)]
	
	def GetFrequencyPower(self, buffer, frequency):
		return frequencyCrossCorrelations.matchQuality(buffer, frequency)
		
	def OnNewBuffer(self, buffer, sampleInterval):
		powers = [self.GetFrequencyPower(buffer, f) for f in self.frequencies]
		
		#pylab.plot(self.frequencies, powers); pylab.grid(True); pylab.show()
		
		maxIndex = powers.index(max(powers))
		noiseFrequency = self.frequencies[maxIndex]
		newInterval = sampleInterval * 60.0 / self.frequencies[maxIndex]
		#print self.frequencies[maxIndex], newInterval
		return newInterval, newInterval
		
class HybridGoertzelRandom:
	def __init__(self, sampleInterval):
		self.FirstLoop = True
		self.geortzel = GoertzelValues(sampleInterval)
		
		
	def OnNewBuffer(self, buffer, sampleInterval):
		if self.FirstLoop:
			self.FirstLoop = False
			result = self.geortzel.OnNewBuffer(buffer, sampleInterval)
			self.randomLeap = RandomLeapKeepBest(result[0], leapSize = 0.01, decayPow = 0.8)
			return result
		else:
			return self.randomLeap.OnNewBuffer(buffer, sampleInterval)
		
def ConvergeFunc(algorithm, initialOffset):
	return TestConvergence(algorithm, plot = False, initialOffset = initialOffset, printStatements = False)
		
def GetExpectedError(algorithmClass, n = 1000):
	import multiprocessing
	
	pool = multiprocessing.Pool(7)
	
	partialConverge = functools.partial(ConvergeFunc, algorithmClass)
	
	offsets = [10*(random() - 0.5) for _ in xrange(n)]
	leakages = []
	for i, leakage in enumerate(pool.imap(partialConverge, offsets), 1):
		sys.stderr.write('\rdone {0:%}'.format(float(i)/n))
		leakages.append(leakage)
	
	#print leakages
	print '\r%s: Average error: %f \t+/-: %f' % (algorithmClass.__name__, stats.mean(leakages), stats.stdDev(leakages))
		
def TestQuadraticGuessAccuracy(rawData, n):
	partial = functools.partial(QuadraticGuessIteration, rawData)
	
	results = map(lambda x: partial(), xrange(n))
	
	errors = map(lambda x: x[1] - x[0], results)
	
	pylab.hist(errors, bins = 50)
	pylab.show()

def QuadraticGuessIteration(rawData):
	fDown = 8000.0 + 200.0 * (random() - 0.5)
	rawSps = fDown; rawData = fftDataExtraction.downSample(rawData, 32000, fDown, interpolate = False)[int(random() * 100):]
	calculatedSampleRate = (59.96 / 60.0 * samplesPerSecond * rawSps / fDown)
	
	algorithm = QuadraticErrorFitting2(0)
	
	testSampleInterval = algorithm.GetFirstInterval()
	testIntervalCounter = 0.0
	
	testBufferNewAmount = windowSize
	
	testBuffer = []
	
	testLeakages = []; testLeakageTimes = []
	testSampleRates = []
	
	lastSample = 0.0
	
	for index, sample in enumerate(rawData):
		time = float(index) / rawSps
		
		testIntervalCounter += 1.0
			
		if testIntervalCounter >= testSampleInterval:
			testIntervalCounter %= testSampleInterval
			weight0 = min(1.0, testIntervalCounter)
			weight1 = max(0.0, 1.0 - testIntervalCounter)
			interpolatedSample = weight0 * sample + weight1 * lastSample
			testBuffer.append(interpolatedSample)
			
			if len(testBuffer) > windowSize + testBufferNewAmount:
				testBuffer = testBuffer[-windowSize:]
				
				leakage = getToneLeakage(testBuffer)
				testLeakages.append(leakage)
				testLeakageTimes.append(time)
				testSampleRates.append(float(rawSps) / testSampleInterval)
				
				realSampleInterval, testSampleInterval, isDone = algorithm.OnNewBuffer(testBuffer, testSampleInterval, True)
				if isDone:
					#print testSampleInterval
					break
					
	return calculatedSampleRate, rawSps / testSampleInterval
		
def TestConvergence(algorithmClass, plot = True, initialOffset = 2.3, printStatements = True):
	global rawData
	
	realSampleInterval = rawSps / (samplesPerSecond + initialOffset)
	testSampleInterval = realSampleInterval
	
	#algorithm = TestAlgorithm(testSampleInterval)
	#algorithm = RandomLeapKeepBest(testSampleInterval)
	#algorithm = SimulatedAnnealing(testSampleInterval)
	
	algorithm = algorithmClass(testSampleInterval)
	try:
		x = algorithm.GetFirstInterval()
		if x:
			realSampleInterval = x
			testSampleInterval = x
	except Exception, e:
		print e
	
	realIntervalCounter = 0.0; testIntervalCounter = 0.0
	
	realBufferNewAmount = int(windowSize / transformsPerSecond)
	testBufferNewAmount = windowSize
	
	realBuffer = []; testBuffer = []
	
	realLeakages = []; realLeakageTimes = []; testLeakages = []; testLeakageTimes = []
	realSampleRates = []; testSampleRates = []
	
	lastSample = 0.0
	
	for index, sample in enumerate(rawData):
		time = float(index) / rawSps
		
		realIntervalCounter += 1.0
		testIntervalCounter += 1.0
		
		if realIntervalCounter >= realSampleInterval:
			realIntervalCounter %= realSampleInterval
			weight0 = min(1.0, realIntervalCounter)
			weight1 = max(0.0, 1.0 - realIntervalCounter)
			interpolatedSample = weight0 * sample + weight1 * lastSample
			realBuffer.append(interpolatedSample)
			
			if len(realBuffer) > windowSize + realBufferNewAmount:
				realBuffer = realBuffer[-windowSize:]
				
				leakage = getToneLeakage(realBuffer)
				realLeakages.append(leakage)
				realLeakageTimes.append(time)
				
				realSampleRates.append(float(rawSps) / realSampleInterval)
				
			
		if testIntervalCounter >= testSampleInterval:
			testIntervalCounter %= testSampleInterval
			weight0 = min(1.0, testIntervalCounter)
			weight1 = max(0.0, 1.0 - testIntervalCounter)
			interpolatedSample = weight0 * sample + weight1 * lastSample
			testBuffer.append(interpolatedSample)
			
			if len(testBuffer) > windowSize + testBufferNewAmount:
				testBuffer = testBuffer[-windowSize:]
				
				leakage = getToneLeakage(testBuffer)
				testLeakages.append(leakage)
				testLeakageTimes.append(time)
				testSampleRates.append(float(rawSps) / testSampleInterval)
				
				realSampleInterval, testSampleInterval = algorithm.OnNewBuffer(testBuffer, testSampleInterval)
								
		lastSample = sample
	
	result = sum(realLeakages)	
	if printStatements:
		print 'final sample frequency: %f' % (float(rawSps)/realSampleInterval)#, 100.0 * abs(samplesPerSecond -float(rawSps)/realSampleInterval)/samplesPerSecond)
		print 'total leakage: %f' % result
		
	if plot:
		fig = pylab.figure()
		
		f1ax1 = fig.add_subplot(211)
		f1ax1.set_title("Best Sampling Frequency")
		f1ax1.semilogy(realLeakageTimes, realLeakages)
		f1ax2 = f1ax1.twinx()
		f1ax2.plot(realLeakageTimes, realSampleRates, color = 'Red')
		for tick in f1ax2.get_yticklabels(): tick.set_color('Red')
		f1ax1.grid(True)
		
		f2ax1 = fig.add_subplot(212)
		f2ax1.set_title("Current Sampling Frequency")
		f2ax1.semilogy(testLeakageTimes, testLeakages, '-o')
		f2ax2 = f2ax1.twinx()
		f2ax2.plot(testLeakageTimes, testSampleRates, '-o', color = 'Red')
		for tick in f2ax2.get_yticklabels(): tick.set_color('Red')
		f2ax1.grid(True)
		
		pylab.show()
		
	return result

if __name__ == "__main__":

	#totalLeakage = TestConvergence(PeakImbalance)
	#totalLeakage = TestConvergence(RandomLeapKeepBest)
	#totalLeakage = TestConvergence(QuadraticErrorFitting)
	#totalLeakage = TestConvergence(QuadraticErrorFitting2)
	
	print TestQuadraticGuessAccuracy(rawData, 1000)
	

	"""May30 results (n=5000), Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls:
	SimulatedAnnealing: Average error: 1.535507     +/-: 1.606706
	RandomLeapKeepBest: Average error: 1.166930     +/-: 1.307195
	
	May30 n=10000, Generated data
	RandomLeapKeepBest: Average error: 1.061977     +/-: 1.184265
	SimulatedAnnealing: Average error: 1.431364     +/-: 1.506392
	HybridShapeRandom: Average error: 5.130757      +/-: 6.733491
	"""
	
	#GetExpectedError(PeakImbalance)
	#GetExpectedError(SimulatedAnnealing)
	#GetExpectedError(HybridShapeRandom)