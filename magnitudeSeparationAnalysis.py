import stats
import fftDataExtraction
import constants
from math import sqrt
import svmutil

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
	
def svmClassifierAccuracy(fData1, fData2, binsToUse):
	svmData1 = [[x[index] for index in binsToUse] for x in fData1]
	svmData2 = [[x[index] for index in binsToUse] for x in fData2]
	
	svmData = svmData1 + svmData2
	
	svmResult = [0 for _ in range(len(svmData2))] + [1 for _ in range(len(svmData2))]
	
	prob = svmutil.svm_problem(svmResult, svmData)
	param = svmutil.svm_parameter()
	
	param.parse_options('-q')	#quiet
	param.cross_validation = True
	param.nr_fold = 10
	param.kernel_type = svmutil.LINEAR
	param.C = 0.1
	
	accuracy = svmutil.svm_train(prob, param)
	return accuracy
	
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
	
	svmAccuracy = svmClassifierAccuracy(fData1, fData2, bins)
	#print "SVM accuracy: %lf" % svmAccuracy