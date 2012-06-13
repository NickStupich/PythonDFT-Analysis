import dataImport
from matplotlib import pylab
from scipy import signal
import fftDataExtraction

def bandStopFilterData(data, sps, frequencies, log2Taps = 10, fRange = 2.0):
	taps = (1<<log2Taps)+1
	fStops = []
	for f in frequencies:
		fStops.append(f - fRange)
		fStops.append(f + fRange)
		
	filter = signal.firwin(taps, fStops, nyq = sps/2)
	
	result = signal.convolve(filter, data)
	diff = len(result) - len(data)
	result = result[diff/2:-(diff-diff/2)]
	return result

if __name__ == "__main__":

	sampleFreq = 8000.0
	
	data = dataImport.generateSignal(sampleFreq, [(60.0, 1.0)], seconds = 2.0)
	
	#data = dataImport.readADSFile("Data/Mark/32kSPS_160kS_FlexorRadialis_Transitions.xls")
	#data = fftDataExtraction.downSample(data, 32000, sampleFreq, interpolate = False)

	times = [float(x) / sampleFreq for x in range(len(data))]
	
	fs = [60.0, 120.0, 180.0]
	data2 = bandStopFilterData(data, sampleFreq, frequencies = fs, fRange = 2.0, log2Taps = 13)
	
	pylab.subplot(211)
	pylab.plot(times, data)
	
	pylab.subplot(212)
	pylab.plot(times, data2)
	
	pylab.show()