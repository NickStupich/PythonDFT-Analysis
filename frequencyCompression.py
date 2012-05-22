from math import sin, cos, pi
from numpy import complex64 as datatype
from numpy import float32

def dft(timeData, compression = 1.0):
	n = len(timeData)
	result = [datatype(0) for _ in range(n)]
	
	for i in range(n):
		a = float32(compression * 2.0 * pi * i / n)
		for j in range(n):
			result[i] += timeData[j] * complex(cos(a*j), sin(a*j))
			
			
	result = map(lambda x: x/n, result)
	
	return result
	