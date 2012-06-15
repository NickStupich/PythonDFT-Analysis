import dataImport
from matplotlib import pylab
import constants
import fftDataExtraction
import svmutil
import svmAccuracy
import FirFilter

baseFilename = "Data\IndividualFingers/8kSPS_40kS_ExtensorRadialis_%s.xls"
#baseFilename = "Data\IndividualFingers/8kSPS_40kS_FlexorRadialis_%s.xls"
print baseFilename
rawSps = 8000

filterData = False

constants.printConstants()

files = {	"Both" : [1, 1],
			"IndexFinger" : [1, 0],
			"MiddleFinger" : [0, 1],
			"Relaxed" : [0, 0]
			}

def plotTimeDomainSignals(datas):
	times = [float(x) / rawSps for x in range(len(datas[0][0]))]
	numFiles = len(datas)
	numChannels = len(datas[0])
	#pylab.subplot(numFiles * 100 + 11)
	for i, (rawData, output) in enumerate(datas):
		channels = zip(*rawData)
		for j, channel in enumerate(channels):
			pylab.subplot(numFiles * 100 + 10 * (numChannels) + i*2 + j + 1)
			pylab.plot(times, channel)
			pylab.grid(True)
			pylab.title(str(output) + ' chan: %d' % j)
	pylab.show()
	
def getSVMTrainingData(datas):
	trainingDatas = []
	for rawData, output in datas:
		channels = zip(*rawData)
		allBins = []
		for channel in channels:
			downSampledData = fftDataExtraction.downSample(channel, rawSps, constants.samplesPerSecond, interpolate = True)
			
			transforms = fftDataExtraction.applyTransformsToWindows(fftDataExtraction.getFFTWindows(downSampledData), magnitude = True, polyFitSubtraction = 2)
			
			bins = fftDataExtraction.DoFrequencyBinning(transforms)
			allBins.append(bins)
			
		trainingInputs = map(lambda x: x[0] + x[1], zip(*allBins))
		
		trainingDatas += [(input, output) for input in trainingInputs]
		
	return trainingDatas
	
def getSVMAccuracy(trainingData):
	numOutputs = len(trainingData[0][1])
	for outputIndex in range(numOutputs):
		inputs = [input for (input, output) in trainingData]
		outputs = [output[outputIndex] for (input, output) in trainingData]
		
		prob = svmutil.svm_problem(outputs, inputs)
		param = svmAccuracy.getSvmParam(cross_validation_only = True)
		
		model = svmutil.svm_train(prob, param)
		print 'output index: %d - %s\n' % (outputIndex, {0 : "Index", 1: "Middle"}[outputIndex])
			
if __name__ == "__main__":
	datas = []
	
	for f in files:
		output = files[f]
		filename = baseFilename % f
		rawData = dataImport.readADSFile(filename, channels = len(output))
		if filterData:
			channels = zip(*rawData)
			filteredChannels = []
			for channel in channels:
				filteredChannels.append(FirFilter.bandStopFilterData(channel, rawSps, [60.0, 120.0, 180.0], log2Taps = 13))
				print 'filtered'
			rawData = zip(*filteredChannels)
		
		datas.append((rawData, output))
		
	#plotTimeDomainSignals(datas)
	trainingData = getSVMTrainingData(datas)
	getSVMAccuracy(trainingData)