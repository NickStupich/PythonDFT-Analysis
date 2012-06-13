import dataImport
from matplotlib import pylab
import fftDataExtraction

if __name__ == "__main__":
	filename = "Data/Mark/32kSPS_160kS_FlexorRadialis_Transitions.xls"
	
	data = dataImport.readADSFile(filename)
	data = data[40000:60000]
	
	data = fftDataExtraction.subtractPolynomialFit(data, 3)
	pylab.plot(range(len(data)), data)
	pylab.show()