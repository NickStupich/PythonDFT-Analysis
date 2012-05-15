from numpy.fft import rfft as fourier
from numpy import absolute
from math import sin, pi, log10
from matplotlib import pylab

testNums = [1, 2, 2, 1]

def generateTimeDomain(times, frequencies):
	result = [0] * len(times)
	
	for i, t in enumerate(times):
		for (freq, amp) in frequencies:
			result[i] += sin(2.0 * pi * t * freq) * amp
	
	return result
	
def generateTimes(sampleFreq, numSamples):
	return [float(t) / sampleFreq for t in range(numSamples)]
	
def generateFFTFrequencies(sampleFreq, numSamples):
	binWidth = sampleFreq / numSamples
	return [i * binWidth for i in range(numSamples/2+1)]
	
def toDb(x):
	return 20 * log10(x)
	
def main():
	numSamples = 256
	sampleFreq = 1024

	times = generateTimes(sampleFreq, numSamples)
	timeData = generateTimeDomain(times, [(81, 1)])#, (90, 0.5)])
	
	pylab.plot(times, timeData); pylab.show()
	
	freqData = map(absolute, fourier(timeData))
	freqDb = map(toDb, freqData)
	
	frequencies = generateFFTFrequencies(sampleFreq, numSamples)
	print 'bin size: %s' % frequencies[1]
	pylab.plot(frequencies, freqDb); pylab.show()
	
if __name__ == "__main__":
	main()