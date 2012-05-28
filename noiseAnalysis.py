import dataImport
from numpy.fft import rfft as fourier
from numpy import absolute
import plotting
from matplotlib import pylab
from math import log10, log
import fftDataExtraction

#filename = "NoiseData/2 loops.xls"
#filename = "NoiseData/10 loops.xls"
filename = "NoiseData/6 Loops 8000SPS Volts.xls"
#filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls"

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
	
if __name__ == "__main__":
	rawSps = 8000
		
	data = dataImport.readADSFile(filename)
	#getBits(data)
	
	startOffset = 7
	allData = []
	for offset in range(0, len(data), 1000):
		
		xs  =[]
		ys = []
		
		for sps in range(600, 1000):
			downSampledData = fftDataExtraction._downSample(data, rawSps, sps)[offset+startOffset:offset+128+startOffset]
			print sps, offset
			frequencies = [float(sps) * x / len(downSampledData) for x in range(len(downSampledData)/2+1)]
			fData = map(absolute, fourier(downSampledData))
			
			leakage = sum([x for x, f in zip(fData, frequencies) if abs(f % 60) > 1.0])
			#print 'leakage: %f' % leakage
			#plot(fData, frequencies)
			#print '%d - %f' % (sps, leakage)
			xs.append(sps)
			ys.append(leakage)
		
		allData.append(ys)
			
	#pylab.subplot(211)
	for ys in allData:
		pylab.plot(xs, ys)
		
	
	pylab.show()
	