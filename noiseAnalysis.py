import dataImport
from numpy.fft import rfft as fourier
from numpy import absolute
import plotting
from matplotlib import pylab
from math import log10

filename = "NoiseData/2 loops.xls"
#filename = "NoiseData/10 loops.xls"

def plot(fData, frequencies):
	
	fData = map(log10, fData)
	
	#cutoff to lower frequencies - 200Hz max
	index = int(200.0 / frequencies[1])
	frequencies = frequencies[1:index]
	fData = fData[1:index]
	
	pylab.plot(frequencies, fData)
	pylab.grid(True)
	pylab.show()

if __name__ == "__main__":
	sps = 32000
		
	for l in range(159000, 160001, 10):
		data = dataImport.readADSFile(filename)[:l]
		frequencies = [float(sps) * x / len(data) for x in range(len(data)/2+1)]
		fData = map(absolute, fourier(data))
		
		leakage = sum([x for x, f in zip(fData, frequencies) if abs(f % 60) > 1.0])
		#print 'leakage: %f' % leakage
		#plot(fData, frequencies)
		
		print '%d - %f' % (l, leakage)