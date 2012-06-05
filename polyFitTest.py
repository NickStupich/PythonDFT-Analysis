"""from numpy import polyfit, poly1d, linspace
from matplotlib import pylab

x = [1, 2, 3, 4, 5, 6, 7]
y = [1, 4, 9, 16, 25, 36, 60]
weights = [1, 1, 1, 1, 1, 1, 1]

z = polyfit(x, y, 2, w = weights, full = True)
p = poly1d(z[0])

print z
xp = linspace(0, 10, 100)
pylab.plot(x, y, '.', xp, p(xp), '-')
pylab.grid(True)
pylab.show()"""

import numpy

def polynomialFit(x, y, order = 3, errors = None):

	n = len(x)
	
	if errors is None:
		errors = [1] * n
	
	A = numpy.matrix([[(x[i] ** j) / errors[i] for j in range(order)] for i in range(n)])
	b = numpy.matrix([y[i] / errors[i] for i in range(n)]).transpose()
	At = A.transpose()
	alpha = At.dot(A)
	beta = At.dot(b)
	
	C = alpha.getI()
	
	print C
	
	coefs = C * beta
	return coefs.transpose().tolist()[0]
	
if __name__ == "__main__":
	"""
	x = [0, 1, 2, 3]
	y = [3, 4, 5, 6]
	print polynomialFit(x, y, 2)
	"""
	
	x = [0, 1, 2, 3, 4]
	y = [1, 2, 5, 10, 18]
	errors = [1] * 5
	print polynomialFit(x, y, 3, errors)