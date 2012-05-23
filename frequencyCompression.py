from math import sin, cos, pi
from numpy import complex128 as datatype
from numpy import float64 as floatType

def dft(timeData, compression = 1.0):
	n = len(timeData)
	result = [datatype(0.0) for _ in range(n)]
	
	for i in range(n):
		for j in range(n):
			result[i] += timeData[j] * complex(cos(compression * 2.0 * pi * i / n*j), sin(compression * 2.0 * pi * i / n*j))
			
			
	result = map(lambda x: x/n, result)
	
	return result
	