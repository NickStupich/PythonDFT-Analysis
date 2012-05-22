import os

def readADSFile(filename):
	return [float(x) for x in open(filename).read(
).split('CH1')[-1].strip('\n').split('\n') if len(x) > 5]