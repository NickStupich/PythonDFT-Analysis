import fftDataExtraction
import constants
from matplotlib import pylab


if __name__ == "__main__":
	filename = "Data/Mark/32kSPS_160kS_ExtensorRadialis_0%.xls"
	data = fftDataExtraction.getDownSampledData(filename)
	sps = constants.samplesPerSecond
	windows = fftDataExtraction.getFFTWindows(data[int(0.8*sps):])
	
	alltimes = [float(x) / sps for x in range(len(data))]
	times =  range(len(windows[0]))
	postData = fftDataExtraction.subtractPolynomialFit(windows[0], 5)
	#pylab.plot(alltimes, data)
	pylab.plot(times, windows[0])
	pylab.plot(times, postData)
	pylab.grid(True)
	pylab.show()