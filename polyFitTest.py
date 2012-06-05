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
from matplotlib import pylab
import math

def polynomialFit(x, y, order = 3, errors = None, returnErrors = False):

	n = len(x)
	
	if errors is None:
		errors = [1.0] * n
	
	A = numpy.matrix([[(float(x[i]) ** float(j)) / float(errors[i]) for j in range(order)] for i in range(n)])
	b = numpy.matrix([float(y[i]) / float(errors[i]) for i in range(n)]).transpose()
	At = A.transpose()
	alpha = At.dot(A)
	
	print alpha
	beta = At.dot(b)
	
	C = alpha.getI()#inverse
	
	#print C
	
	coefs = C * beta
	if returnErrors:
		return coefs.transpose().tolist()[0], C
	else:
		return coefs.transpose().tolist()[0]
	
if __name__ == "__main__":
	"""
	x = [0, 1, 2, 3]
	y = [3, 4, 5, 6]
	print polynomialFit(x, y, 2)
	"""
	
	x = [0, 1, 2, 3, 5]
	y = [3, 4, 7, 14, 29]
	errors = [1.0, 1.0, 1.0, 1.0, 1.0]
	order = 3
	coefs, C = polynomialFit(x, y, order, errors, returnErrors = True)
	print coefs
	print C
	
	axis = pylab.axes()
	
	xp = numpy.linspace(0, 10, 100)
	p = numpy.poly1d(coefs[::-1])
	yp = p(xp)
	
	axis.plot(x, y, '-o')
	axis.plot(xp, yp, '-')
	
	axis.grid(True)
	
	
	axis2 = axis.twinx()
	
	xis = numpy.linspace(0, 10, 100)
	yis = []
	for xi in xis:
		Xi = numpy.matrix([xi**n for n in range(order)])
		#print C.dot(Xi)
		errs = C.dot(Xi.transpose()).tolist()[0]
		
		#print errs
		err = math.sqrt(sum(map(lambda x: x*x, errs)))
		yis.append(err)
	
	axis2.plot(xis, yis, 'red')
	#pylab.show()
	
	pylab.show()
	
	