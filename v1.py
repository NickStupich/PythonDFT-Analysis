from numpy.fft import rfft as fourier
from numpy import absolute
from math import sin, pi, log10
from matplotlib import pylab
from numpy import float32 as dtype

numSamples = 128
sampleFreq = 768

def generateTimeDomain(times, frequencies):
	result = [0] * len(times)
	
	for i, t in enumerate(times):
		for (freq, amp) in frequencies:
			result[i] += sin(2.0 * pi * t * freq) * amp
	
	result = map(dtype, result)
	return result
	
def generateTimes(sampleFreq, numSamples):
	return [float(t) / sampleFreq for t in range(numSamples)]
	
def generateFFTFrequencies(sampleFreq, numSamples):
	binWidth = sampleFreq / numSamples
	return [i * binWidth for i in range(numSamples/2+1)]
	
def toDb(x):
	return 20 * log10(x)
	
def plot(x, y, semilogx = False):
	if semilogx:
		pylab.semilogx(x, y)
	else:
		pylab.plot(x, y)
		
	pylab.grid(True)
	pylab.show()
	
def compareFrequencies():
	times = generateTimes(sampleFreq, numSamples)
	signal = (80.0, 0.1)
	coherent = (50.0, 1.0)
	incoherent = (51.0, 1.0)
	highFNoise = (500.0, 0.01)
	timeData = generateTimeDomain(times, [signal, coherent, highFNoise])
	timeData2 = generateTimeDomain(times, [signal, incoherent, highFNoise])
	timeData3 = generateTimeDomain(times, [signal, highFNoise])
	
	#timeData = generateTimeDomain(times, [(60.0, 1.0)])
	#timeData2 = generateTimeDomain(times, [(61.0, 1.0)])
	
	roi = (0, 20)
	
	freqData = map(toDb, map(dtype, map(absolute, fourier(timeData))))[roi[0]:roi[1]]
	freqData2 = map(toDb, map(dtype, map(absolute, fourier(timeData2))))[roi[0]:roi[1]]
	freqData3 = map(toDb, map(dtype, map(absolute, fourier(timeData3))))[roi[0]:roi[1]]
	
	frequencies = generateFFTFrequencies(sampleFreq, numSamples)[roi[0]:roi[1]]
	
	#pylab.subplot(111)
	pylab.plot(frequencies, freqData)
	
	#pylab.subplot(112)
	pylab.plot(frequencies, freqData2)
	
	pylab.plot(frequencies, freqData3)
	
	pylab.grid(True)
	pylab.show()
	
def test1():
	times = generateTimes(sampleFreq, numSamples)
	timeData = generateTimeDomain(times, [(50.0, 1.0)])
	
	#plot(times, timeData)
	
	freqData = map(toDb, map(dtype, map(absolute, fourier(timeData))))
	
	frequencies = generateFFTFrequencies(sampleFreq, numSamples)
	print 'bin size: %s' % frequencies[1]
	
	#plot(frequencies, freqData, False)
	plot(frequencies[:15], freqData[:15], False)
	
def main():
	
	#compareFrequencies()
	test1()
	
if __name__ == "__main__":
	main()