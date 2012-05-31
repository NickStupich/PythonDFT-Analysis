from math import sin, cos, pi
from numpy import complex128 as datatype
from numpy import float64 as floatType
import dataImport
from numpy import absolute
from matplotlib import pylab

def dft(timeData, compression = 1.0):
	n = len(timeData)
	result = [datatype(0.0) for _ in range(n)]
	
	for i in range(n):
		for j in range(n):
			result[i] += timeData[j] * complex(cos(compression * 2.0 * pi * i / n*j), sin(compression * 2.0 * pi * i / n*j))
			
			
	result = map(lambda x: x/n, result)
	
	return result
	
if __name__ == "__main__":
	pylab.subplot(211)
	length = 1.0 / 6
	sps = 768.0
	compression = 0.2
	data = dataImport.generateSignal(sps, [(60.0, 1.0)], length)
	f = map(absolute, dft(data, compression))
	f = f[:len(f)/2]
	freqs = [compression / length * x for x in range(len(f))]
	
	pylab.plot(freqs, f)
	pylab.grid(True)
	
	pylab.subplot(212)
	length = 1.0 / 6
	sps = 768.0
	compression = 0.2
	data = dataImport.generateSignal(sps, [(60.2, 1.0)], length)
	f = map(absolute, dft(data, compression))
	f = f[:len(f)/2]
	freqs = [compression / length * x for x in range(len(f))]
	
	pylab.plot(freqs, f)
	
	pylab.grid(True)
	
	pylab.show()
	