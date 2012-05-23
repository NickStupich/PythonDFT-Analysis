import stats
import fftDataExtraction
import constants
from math import sqrt

def measureFFTMagnitudeDiff(fData1, fData2, binsToUse):
	meanAndDev1 = getBinMeanAndStdDev(fData1)
	meanAndDev2 = getBinMeanAndStdDev(fData2)
	
	distances = []
	
	for bin in binsToUse:
		mean1, dev1 = meanAndDev1[bin]
		mean2, dev2 = meanAndDev2[bin]
		dist = (mean2-mean1) / sqrt(dev1 *dev1 + dev2 * dev2)
		distances.append(dist)
		
	#print distances
		
	total = stats.mean(distances)
	return total
	
def getBinMeanAndStdDev(freqData):
	bins = [map(lambda x: x[index], freqData) for index in range(len(freqData[0]))]
	means = [stats.mean(bin) for bin in bins]
	stdDevs = [stats.stdDev(bin) for bin in bins]
	
	return zip(means, stdDevs)
	
if __name__ == "__main__":
	fnBase = "Data/Mark/32kSPS_160kS_FlexorRadialis_%d%%.xls"
	#fnBase = "Data/Mark/32kSPS_160kS_ExtensorRadialis_%d%%.xls"
	
	fn1 = fnBase % 0
	fn2 = fnBase % 10
	
	fData1, binSpacing = fftDataExtraction.extractFFTData(fn1, True)
	fData2, binSpacing = fftDataExtraction.extractFFTData(fn2, True)
	
	bins = constants.bins
	
	separation = measureFFTMagnitudeDiff(fData1, fData2, bins)
	print "0%% vs 10%% separation: %f" % separation