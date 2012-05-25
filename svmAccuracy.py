import svmutil
from matplotlib import pylab
import constants
import stats

def printSvmValidationAccuracy(input, output):
	
	prob = svmutil.svm_problem(output, input)
	param = getSvmParam(True)
	
	accuracy = svmutil.svm_train(prob, param)
	return accuracy
	
def getSvmParam(cross_validation_only = False):
	param = svmutil.svm_parameter()
	param.parse_options('-q')	#quiet
	
	if cross_validation_only:
		param.cross_validation = True
		param.nr_fold = 10
	param.kernel_type = svmutil.LINEAR
	param.C = 10.0 ** 2.0
	
	return param
	
def getSVMValidationPredictions(input, output, folds):
	n = len(input)
	predictions = [None] * n
	
	for fold in range(folds):
		testIn = [input[x] for x in range(n) if x % folds == fold]
		testOut = [output[x] for x in range(n) if x % folds == fold]
		
		trainIn = [input[x] for x in range(n) if x % folds != fold]
		trainOut = [output[x] for x in range(n) if x % folds != fold]
		
		testIndeces = range(fold, n, folds)
		
		#print trainIn[0], trainOut[0]
		prob = svmutil.svm_problem(trainOut, trainIn)
		param = getSvmParam()
		model = svmutil.svm_train(prob, param)
		
		labels, acc, vals = svmutil.svm_predict([0] * len(testOut), testIn, model)
		for index, label in zip(testIndeces, labels):
			predictions[index] = label
			
	return predictions
	
def getAverageSVMPredictions(input, output):	
	#get a better measure of actual accuracy at different times by combining predictions from many numbers of folds validation
	allPredictions = [[] for _ in range(len(input))]
	for folds in range(10, 20):
		pred = getSVMValidationPredictions(input, output, folds)
		for i in range(len(pred)):
			allPredictions[i].append(pred[i])
	
	predictions = map(stats.mean, allPredictions)
	return predictions
	
def graphSvmLatency(predictions, output, rawTimeDomainData, fftTimes):
	#use a n fold accuracy type thing, so that n-1 classifiers estimate the output at each point.  Then plot that value
	#vs the time domain data to see when we transition
	
	#do the graphing now
	rawTimes = [1000 * float(x) / constants.samplesPerSecond for x in range(len(rawTimeDomainData))]
	#fftTimes = [1000.0 *(0 * float(constants.windowSize) / constants.samplesPerSecond + float(x) / constants.transformsPerSecond) for x in range(0, len(input))]
	#print zip(fftTimes, output)
	print len(fftTimes), len(output)
	figure = pylab.figure(figsize=(20, 12))
	pylab.subplot(211)
	
	pylab.plot(rawTimes, rawTimeDomainData)
	pylab.plot(fftTimes, map(lambda x: x*0.1+0.1, output), '-o')
	pylab.plot(fftTimes, map(lambda x: x*0.1 + 0.3, predictions), '-o')
	
	pylab.grid(True)
	pylab.subplot(212)
	pylab.specgram(	rawTimeDomainData, 
					NFFT = constants.windowSize,
					Fs = constants.samplesPerSecond, 
					noverlap = constants.samplesPerSecond / constants.transformsPerSecond,
					sides = 'onesided',
					detrend = pylab.detrend_mean
					)
	pylab.grid(True)
	pylab.show()
	