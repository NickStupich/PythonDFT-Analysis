import stats
import fftDataExtraction
import constants
import svmutil
from matplotlib import pylab
import magnitudeSeparationAnalysis
import svmAccuracy
import plotting
import dataImport
import stats

startIndexRange = 0.05	#s = 20ms
dataLength = 0.5
numSignalChunks = 8

def createChangingTimeDomainData(baseFilename, low = 0, high = 10):
	dat0 = fftDataExtraction.getDownSampledData(baseFilename % low)
	dat10 = fftDataExtraction.getDownSampledData(baseFilename % high)
	
	#alternate 1 second of each
	
	correctOutput = []
	allData = []
	
	for i in range(0, len(dat0), constants.samplesPerSecond):
		allData += centerAroundZero(dat0[i:i+constants.samplesPerSecond])
		correctOutput += [0] * constants.samplesPerSecond
		
		allData += centerAroundZero(dat10[i:i+constants.samplesPerSecond])
		correctOutput += [1] * constants.samplesPerSecond
		
	return allData, correctOutput
	
def CrossCorrelation(dat1, dat2):
	if len(dat1) != len(dat2):
		raise Exception("lengths don't match")
		
	result = 0
	for index in range(len(dat1)):
		result += dat1[index] * dat2[index]
		
	return result
	
def getBestStartIndex(oldData, newData, sps):
	#remove between 20 and 40 ms of new data, wherever the cross-correlation is greatest
	correlations = []
	dataLen = int(sps * startIndexRange)
	for startIndex in range(dataLen, 2*dataLen):
		crossCor = CrossCorrelation(oldData[-dataLen:], newData[startIndex:startIndex+dataLen])
		correlations.append((crossCor, startIndex))
		
	#print '\n'.join([str(x) for x in correlations])
	
	#pylab.plot(map(lambda x: x[1], correlations), map(lambda x: x[0], correlations))
	#pylab.show()
	
	#result is more or less a sin() curve, with a dc value overlaid.  we DON'T want to match that dc part, 
	#so if the overall maximum is at either end of the line, don't use that.  We need one in the middle where
	#we know that 60Hz is best matched
	
	while True:
		x = max(correlations)
		if x == correlations[-1]:
			correlations.remove(x)
		elif x == correlations[0]:
			correlations.remove(x)
		else:
			return x[1]
	
def createChangingTimeDomainDataPhaseMatch(baseFilename, low = 0, high = 10):
	dat0 = dataImport.readADSFile(baseFilename % low)
	dat1 = dataImport.readADSFile(baseFilename % high)
	sps = dataImport.getSPS(baseFilename % low)
	if dataImport.getSPS(baseFilename % high) != sps:
		raise Exception("samples per second do not match - FAIL")
	
	dataSources = [dat0, dat1]
	indeces = [0, 0]
	
	if dataLength < float(constants.windowSize) / constants.samplesPerSecond * 1.5:
		raise Exception("Data length is too short - not getting full ffts of a single data source")
	
	numSamples = int(dataLength * sps)
	result = []
	output = []
	
	for i in range(numSignalChunks * 2):
		newIndex = i % 2
			
		if i == 0:
			dataToAppend = centerAroundZero(dataSources[newIndex][indeces[newIndex] : indeces[newIndex] + numSamples])
			indeces[newIndex] += numSamples
		else:
			#gotta phase match
			newData = centerAroundZero(dataSources[newIndex][indeces[newIndex] : int(indeces[newIndex] + numSamples + sps * startIndexRange*2)])
			startOffset = getBestStartIndex(result, newData, sps)
			#print startOffset
			dataToAppend = newData[startOffset: startOffset + numSamples]
			indeces[newIndex] += numSamples + startOffset
			
		if len(dataToAppend) != numSamples:
			raise Exception("Data to be appended is not the correct length")
		
		oldIndex = len(result)
		result += dataToAppend
		output += [newIndex] * numSamples
		
		"""times = range(len(result))
	pylab.subplot(211)
	pylab.plot(times, result)
	pylab.subplot(212)
	pylab.specgram(	result, 
					NFFT = 1024,
					Fs = sps, 
					noverlap = 768,
					sides = 'onesided',
					detrend = pylab.detrend_mean
					)
	pylab.show()
	"""
		
	#down sample result and output
	result = fftDataExtraction._downSample(result, sps)
	output = fftDataExtraction._downSample(output, sps)
	"""
	times = range(len(result))
	pylab.subplot(211)
	pylab.plot(times, result)
	pylab.subplot(212)
	pylab.specgram(	result, 
					NFFT = constants.windowSize,
					Fs = constants.samplesPerSecond, 
					noverlap = constants.samplesPerSecond / constants.transformsPerSecond,
					sides = 'onesided',
					detrend = pylab.detrend_mean
					)
	pylab.show()
	"""
	return result, output
	
def centerAroundZero(timeData):
	#line of best fit, then subtract that
	xValues = range(len(timeData))
	slope, yint = stats.lineOfBestFit(xValues, timeData)
	result = [y-yint-x*slope for x, y in zip(xValues, timeData)]
	return result
	
def getFFTWindows(timeData, output):
	
	fDataResult = []
	outputResult = []
	outputTimes = []
	
	windowOffset = int(constants.samplesPerSecond / constants.transformsPerSecond)
	for i in range(0, int(len(timeData) - constants.windowSize), windowOffset):
		fDataResult.append(timeData[i:i+constants.windowSize])
		outputResult.append(output[i+constants.windowSize])
		outputTimes.append(1000.0 / constants.samplesPerSecond * (i + constants.windowSize))
		#print i, i+constants.windowSize
	
	times = [1000 * x / constants.samplesPerSecond for x in range(len(timeData))]
	#pylab.plot(times, output)
	#pylab.plot(times, timeData)
	#pylab.plot(outputTimes, outputResult)
	#pylab.grid(True)
	#pylab.show()	
	
	return fDataResult, outputResult, outputTimes
	
def squareWave(period, riseDelay, fallDelay, outputTimes):
	result = []
	for time in outputTimes:
		cycleTime = (float(time) / period) % 1000.0
		if cycleTime < float(fallDelay) or cycleTime > 500.0 + float(riseDelay):
			x = 1
		else:
			x = 0
		result.append(x)
	return result
	
def measureLatency(predictions, outputs, outputTimes):
	#find the difference between predictions and outputs while varying the rise and fall times of outputs, look for best match
	
	riseDelayScores = []
	for riseDelay in range(-100, 200, 5):
		sqWave = squareWave(dataLength * 2, riseDelay, 0.0, outputTimes)		
		score = stats.Rmse(sqWave, predictions)
		riseDelayScores.append((score, riseDelay))
		
	riseDelay = min(riseDelayScores)[1]
	
	fallDelayScores = []
	for fallDelay in range(-100, 200, 5):
		sqWave = squareWave(dataLength * 2, riseDelay, fallDelay, outputTimes)
		score = stats.Rmse(sqWave, predictions)
		fallDelayScores.append((score, fallDelay))
		
	fallDelay = min(fallDelayScores)[1]
	
	sqWave = squareWave(dataLength * 2, riseDelay, fallDelay, outputTimes)
	
	#pylab.plot(outputTimes, sqWave, '-o') ;pylab.plot(outputTimes, predictions, '-o') ;pylab.plot([0.0, 0.0], [1.5, -0.5]) ;pylab.show()
	
	return riseDelay, fallDelay
	
	
if __name__ == "__main__":
	constants.samplesPerSecond = int(constants.samplesPerSecond)
	
	#timeData, output = createChangingTimeDomainData(constants.baseFilename, low = 0, high = 10)
	timeData, output = createChangingTimeDomainDataPhaseMatch(constants.baseFilename, low = constants.lowPercent, high = constants.highPercent)
	
	dataWindows, outputs, outputTimes = getFFTWindows(timeData, output)
	transforms = fftDataExtraction.applyTransformsToWindows(dataWindows, True)
	transforms = fftDataExtraction.DoFrequencyBinning(transforms)
	
	#svmAccuracy.printSvmValidationAccuracy(transforms, outputs)
	predictions = svmAccuracy.getAverageSVMPredictions(transforms, outputs)
	
	riseLat, fallLat = measureLatency(predictions, outputs, outputTimes)
	print 'rising latency: %dms' % riseLat
	print 'falling latency: %dms' % fallLat
	
	svmAccuracy.graphSvmLatency(predictions, outputs, timeData, outputTimes)
	
	