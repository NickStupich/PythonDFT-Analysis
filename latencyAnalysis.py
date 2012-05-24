import stats
import fftDataExtraction
import constants
import svmutil
from matplotlib import pylab
import magnitudeSeparationAnalysis
import svmAccuracy
import plotting

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
	
if __name__ == "__main__":
	baseFn = "Data/Mark/32kSPS_160kS_FlexorRadialis_%d%%.xls"
	#baseFn = "Data/Mark/32kSPS_160kS_ExtensorRadialis_%d%%.xls"
	timeData, output = createChangingTimeDomainData(baseFn, low = 0, high = 10)
	
	dataWindows, outputs, outputTimes = getFFTWindows(timeData, output)
	transforms = fftDataExtraction.applyTransformsToWindows(dataWindows, True)
	transforms = fftDataExtraction.DoFrequencyBinning(transforms)
	
	#svmAccuracy.printSvmValidationAccuracy(transforms, outputs)
	svmAccuracy.graphSvmLatency(transforms, outputs, timeData, outputTimes)
	