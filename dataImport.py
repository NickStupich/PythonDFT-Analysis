import os
from math import cos, pi, sin
import random

def readADSFile(filename):
	return [float(x) for x in open(filename).read(
).split('CH1')[-1].strip('\n').split('\n') if len(x) > 5]

def getSPS(filename):
	return int(filename.split('kSPS')[0].split('/')[-1]) * 1000
	
def generateSignal(rawSps, frequencies, seconds = 5.0, noise = 0.0):
	result = [0] *int( seconds * rawSps)
	for f, a in frequencies:
		for index in range(len(result)):
			result[index] += sin(2.0 * pi * index * f / rawSps) * a + random.gauss(0.0, noise)
			
			
	return result