from matplotlib import pylab
from numpy import absolute
import collections
import constants

def plotFrequencyDomain(data, binSpacing, semilogX = False, semilogY = False):
	if not isinstance(data[0], int) and not isinstance(data[0], float):
		data = map(absolute, data)
	
	plotFunc = pylab.plot
	
	if semilogX and semilogY:
		plotFunc = pylab.loglog
	elif semilogX:
		plotFunc = pylab.semilogx
	elif semilogY:
		plotFunc = pylab.semilogy
	
	if isinstance(data[0], collections.Iterable):
		frequencyBins = [float(i) * binSpacing for i in range(len(data[0]))]
		for spectrum in data:
			if not isinstance(spectrum[0], int) and not isinstance(spectrum[0], float):
				x = map(absolute, spectrum)
			else:
				x = spectrum[:]
			plotFunc(frequencyBins, x)
	else:
		frequencyBins = [float(i) * binSpacing for i in range(len(data))]
		print type(data[0])
		if not isinstance(data[0], int) and not isinstance(data[0], float):
			x = map(absolute, data)
		else:
			x = data[:]
		plotFunc(frequencyBins, x)
	
	pylab.grid(True)
	pylab.show()
	
def plotSpectrogram(timeDomainData):
	pylab.specgram(	timeDomainData, 
					NFFT = constants.windowSize,
					Fs = constants.samplesPerSecond, 
					noverlap = constants.samplesPerSecond / constants.transformsPerSecond,
					sides = 'onesided',
					detrend = pylab.detrend_mean
					)
	pylab.show()
					