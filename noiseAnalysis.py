import dataImport
from numpy.fft import rfft as fourier
from numpy import absolute, polyfit
import plotting
from matplotlib import pylab
from math import log10, log, floor, ceil
import fftDataExtraction
import stats
import constants

#filename = "NoiseData/2 loops.xls"
#filename = "NoiseData/10 loops.xls"
#filename = "NoiseData/6 Loops 8000SPS Volts.xls"; rawSps = 8000
filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_10%.xls"; rawSps = 32000

def plot(fData, frequencies):
	
	fData = map(log10, fData)
	
	#cutoff to lower frequencies - 200Hz max
	index = int(200.0 / frequencies[1])
	frequencies = frequencies[1:index]
	fData = fData[1:index]
	
	pylab.plot(frequencies, fData)
	pylab.grid(True)
	pylab.show()

def getBits(data):
	values = {}
	for dat in data:
		if not values.has_key(dat):
			values[dat] = 0
		values[dat] +=1
		
	l = sorted(values.keys())
	print len(values)
	print l[:10]
	#print 1000000.0 * (l[2] - l[1])
	
	diffs = []
	for index in range(len(l)-1):
		diffs.append(1000000*(l[index+1] - l[index]))
		
	increment = min(diffs)
	bits = log(4000000.0 / increment, 2.0)
	print 'bits estimate: %f' % bits
	
def ConvergeOnCoherentSampling(rawData, rawSps):
	sampleInterval = rawSps / (constants.samplesPerSecond + 5.0)
	intervalCounter = 0.0
	
	bufferOverlap = constants.windowSize / constants.transformsPerSecond
	
	buffer = []
	
	lastSample = 0.0
	dir = 0
	lastDir = 0
	intervalChangeSize = sampleInterval * 0.005
	
	for sample in rawData:
		intervalCounter += 1.0
		if intervalCounter >= sampleInterval:
			intervalCounter %= sampleInterval
			weight0 = intervalCounter
			weight1 = 1.0 - intervalCounter
			
			interpolatedSample = weight0 * sample + weight1 * lastSample
			
			buffer.append(interpolatedSample)
			
			if len(buffer) == constants.windowSize + bufferOverlap:
				buffer = buffer[bufferOverlap :]
				
				freqData = fourier(buffer)
				#freqResolution = rawSps /( constants.windowSize * sampleInterval)
				freqResolution = constants.samplesPerSecond / constants.windowSize
				
				lowIndex = 60/freqResolution - 1
				highIndex = 60/freqResolution + 1
				
				lowMagnitude = absolute(freqData[9]) + absolute(freqData[8]) + absolute(freqData[7])
				highMagnitude = absolute(freqData[11]) + absolute(freqData[12]) + absolute(freqData[13])
				
				if lowMagnitude < highMagnitude:
					dir = 1
				elif lowMagnitude > highMagnitude:
					dir = -1
				else:
					dir = 0
				
				if dir * lastDir < 0:
					intervalChangeSize *= 0.9
				
				sampleInterval -= dir * intervalChangeSize
				lastDir = dir
				
				print sampleInterval
				
		lastSample = sample
	
def PlotSpillageVsSampleFrequency(rawData, rawSps):
	startOffset = 7
	allData = []
	start = 748
	end = 488
	for offset in range(0, 2500, 100):
		
		xs  =[]
		ys = []
		
		for sps in range(748, 788, 1):
			#sps /= 10.0
			downSampledData = fftDataExtraction.downSample(data, rawSps, sps)[offset+startOffset:offset+128+startOffset]
			
			#pylab.plot([x/float(sps) for x in range(len(downSampledData))], downSampledData); pylab.show()
			
			#print sps, offset, len(downSampledData)
			frequencies = [float(sps) * x / len(downSampledData) for x in range(len(downSampledData)/2+1)]
			
			leakage = getToneLeakage(downSampledData)
			#print 'leakage: %f' % leakage
			#plot(fData, frequencies)
			#print '%d - %f' % (sps, leakage)
			xs.append(sps)
			ys.append(leakage)
		
		allData.append(ys)
			
	pylab.subplot(211)
	for ys in allData:
		pylab.plot(xs, ys)
	
	means = map(stats.mean, zip(*allData))
	pylab.subplot(212)
	pylab.plot(xs, means, '-o')
	pylab.grid(True)
	
	order = 2
	
	coefficients = polyfit(xs, means, order)
	print coefficients, stats.quadraticMinimum(*coefficients)
	generated = []
	for x in xs:
		y = sum([(float(x)**float(order - i)) * c for i, c in enumerate(coefficients)])
		#print x,y
		generated.append(y)
		
	diff = sum([(x1-x2)**2.0 / x1 for x1, x2 in zip(generated, means)])
	print start, end, diff
		
	#pylab.plot(xs, generated)	
	
	
	pylab.show()
	
def PlotSpillageVsNoiseFrequency():
	frequencies = [x/100.0 for x in range(5980, 6020)]
	allData = [[] for _ in frequencies]
	sps = 768
	xs  =[]
		
	for i, noiseFreq in enumerate(frequencies):
		data = dataImport.generateSignal(rawSps, [(noiseFreq, 1.0)])
		startOffset = 7
		for offset in range(0, 2500, 100):
		
			downSampledData = fftDataExtraction.downSample(data, rawSps, sps)[offset+startOffset:offset+128+startOffset]
			
			#pylab.plot([x/float(sps) for x in range(len(downSampledData))], downSampledData); pylab.show()
			
			#print sps, offset, len(downSampledData)
			#frequencies = [float(sps) * x / len(downSampledData) for x in range(len(downSampledData)/2+1)]
			
			leakage = getToneLeakage(downSampledData)
			#print 'leakage: %f' % leakage
			#plot(fData, frequencies)
			#print '%d - %f' % (sps, leakage)
			allData[i].append(leakage)
	
			
	pylab.subplot(211)
	for ys in zip(*allData):
		pylab.plot(frequencies, ys)
	pylab.grid(True)
	means = map(stats.mean, allData)
	pylab.subplot(212)
	pylab.grid(True)
	pylab.plot(frequencies, means, '-o')
	
	pylab.show()
	
def getToneLeakage(downSampledData, binningType = 1):
	fData = map(lambda x: x*x, map(absolute, fourier(downSampledData)))
	#pylab.semilogy(frequencies, fData); pylab.show()
	
	#leakage = sum([x for x, f in zip(fData, frequencies) if abs(f % 60.0) > 5.0])
	#bins = constants.bins
	
	#bins = [9, 11]	
	#leakage = sum([fData[x] for x in constants.bins])
	
	if binningType == 0:
		leakage = sum([fData[i] for i in range(len(fData)) if i != 10]) / fData[10]
	elif binningType == 1:
		leakage = (fData[9] + fData[11]) / fData[10]
	elif binningType == 2:
		leakage = fData[9] /fData[10]
	elif binningType == 3:
		leakage = fData[11] / fData[10]
	
	return leakage
	
def PlotFreqDomain(rawData, rawSps, sps):
	data = fftDataExtraction.downSample(data, rawSps, sps)
	
	
if __name__ == "__main__":
		
	#data = dataImport.readADSFile(filename)
	data = dataImport.generateSignal(rawSps, [(60.0, 1.0)])#, (120.0, 0.5), (180.0, 0.8)])
	
	PlotSpillageVsSampleFrequency(data, rawSps)
	#PlotSpillageVsNoiseFrequency()
	#ConvergeOnCoherentSampling(data, rawSps)
	#PlotFreqDomain(data, rawSps, 770)
	
	"""
	fData = map(absolute, fourier(data[:7192]))
	print fData[0]
	freqs = range(len(fData))
	
	pylab.semilogy(freqs, fData)
	pylab.show()
	
	
	print len(data)
	"""
	
	