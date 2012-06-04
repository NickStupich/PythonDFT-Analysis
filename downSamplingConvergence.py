import dataImport
import fftDataExtraction
import stats
from matplotlib import pylab
from numpy import polyfit
from random import random

"""
32kSPS_160kS_FlexorRadialis_0%.xls, downsampled to 120SPS
Using variance of difference signal
Buffer length	Frequencies		Difference
20				113.1, 127.3	14.2
40				116.5, 123.6	7.1
60				117.6, 122.3	4.7
80				118.2, 121.7	3.5
100				118.55, 121.35	2.8
120				118.8, 121.1	2.3
240				119.37, 120.54	1.17


20				113.4, 127.3	13.9
40				116.6, 123.5	6.9
60				117.7, 122.2	4.5
80				118.2, 121.6	3.4
100				118.6, 121.3	2.7
120				118.8, 121.1	2.3
240				119.38, 120.51	1.13

"""

MAX_SAMPLES_TO_KEEP = 120	#2 seconds worth of data

def GetSignalCoherenceError(buffer):
	highSamples = buffer[::2]
	lowSamples = buffer[1::2]
	differences = map(lambda x: (x[0]-x[1])**1.0, zip(highSamples, lowSamples))
	return abs(max(differences) - min(differences))
	#return stats.variance(differences)
	#return sum([(differences[i+1] - differences[i])**2.0 for i in range(len(differences)-1)])


allErrors = []
	
"""
f1Last = None
f2Last = None
mu = 0.3
def GetNextGuess1(buf1, buf2, f1, f2, bufLength):
	global f1Last, f2Last
	err1 = GetSignalCoherenceError(buf1)/bufLength
	err2 = GetSignalCoherenceError(buf2)/bufLength

	allErrors.append((f1, err1))
	allErrors.append((f2, err2))
	
	if f1Last and f2Last:
		#less aggressive newton's method
		nf1 = f1 - err1 * (f1 - f1Last[0]) / (err1 - f1Last[1]) 
		nf2 = f2 - err2 * (f2 - f2Last[0]) / (err2 - f2Last[1]) 
	else:
		nf1 = f1 * (1.0 - mu) + f2 * mu
		nf2 = f2 * (1.0 - mu) + f1 * mu

	f1Last = (f1, err1)
	f2Last = (f2, err2)
		
	print nf1, nf2	
	
	return nf1, nf2
"""	

mu = 0.2
def GetNextGuess2(buf1, buf2, f1, f2, bufLength):
	err1 = GetSignalCoherenceError(buf1)/bufLength
	err2 = GetSignalCoherenceError(buf2)/bufLength
	
	allErrors.append((f1, err1))
	allErrors.append((f2, err2))
	
	if err1 > err2:
		f1 += (f2-f1)*mu
	else:
		f2 += (f1-f2)*mu
	
	print f1, f2, err1, err2
	return f1, f2
	
def TestConvergence(rawData, rawSps):
	f1 = 118.0
	f2 = 122.0
	
	c1 = 0.0; c2 = 0.0
	
	buf1 = []; buf2 = []
	
	lastSample = None
	for data in rawData:
		c1 += 1.0
		c2 += 1.0
		
		sp1 = rawSps / f1; sp2 = rawSps / f2
		changed = False
		
		if c1 > sp1:
			c1 %= sp1
			val = data *c1 + lastSample * (1.0 - c1)
			buf1.append(val)
			#buf1 = buf1[-MAX_SAMPLES_TO_KEEP:]
			changed = True
		
		if c2 > sp2:
			c2 %= sp2
			val = data * c2 + lastSample * (1.0 - c2)
			buf2.append(val)
			#buf2 = buf2[-MAX_SAMPLES_TO_KEEP:]
			changed = True
			
		if changed:
			requiredBufferLength = min(MAX_SAMPLES_TO_KEEP, int(150.0 / abs(f2 - f1)))
			#print requiredBufferLength
			
			if len(buf1) > requiredBufferLength and len(buf2) > requiredBufferLength:
				result = GetNextGuess2(buf1[-requiredBufferLength:], buf2[-requiredBufferLength:], f1, f2, requiredBufferLength)
				if result:
					f1, f2 = result
					buf1 = []
					buf2 = []
				else:
					print 'no update'
					pass
				
		lastSample = data
				
if __name__ == "__main__":
	
	filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_0%.xls"; rawSps = 32000
	#filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_0%.xls"; rawSps = 32000
	#filename = "NoiseData/6 Loops 8000SPS Volts.xls"; rawSps = 8000
	#rawData = dataImport.readADSFile(filename)
	f = 60.0
	sps = 8000
	#rawData = fftDataExtraction.downSample(rawData, rawSps, sps, interpolate = False)
	
	rawData = dataImport.generateSignal(sps, [(f, 1.0)], seconds = 30.0)
	TestConvergence(rawData, sps)
	
	x, y = zip(*sorted(allErrors))
	print len(x), len(y)
	pylab.plot(x, y, marker = 'o')
	#coefs = polyfit(x, y, 2)
	#x2 = [min(x) + i * (max(x) - min(x)) / len(x) for i in range(len(x))]
	#y2 = [sum([xi**(2.0-n) * c for n, c in enumerate(coefs)]) for xi in x2]
	#print len(x), len(y2)
	#pylab.plot(x2, y2, '-o')
	
	pylab.grid(True); pylab.show()
	#print stats.mean(centers)
	#print stats.stdDev(centers)