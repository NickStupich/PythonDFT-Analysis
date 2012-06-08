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
from random import random
import stats

def polynomialFit(x, y, order = 3, errors = None, returnErrors = False):

	n = len(x)
	
	if errors is None:
		errors = [1.0] * n
	
	A = numpy.matrix([[(float(x[i]) ** float(j)) / float(errors[i]) for j in range(order)] for i in range(n)])
	b = numpy.matrix([float(y[i]) / float(errors[i]) for i in range(n)]).transpose()
	At = A.transpose()
	alpha = At.dot(A)
	
	#print alpha
	beta = At.dot(b)
	
	C = alpha.getI()#inverse
	
	#print C
	
	coefs = C * beta
	if returnErrors:
		return coefs.transpose().tolist()[0], C
	else:
		return coefs.transpose().tolist()[0]
	
def polynomialFindMinimum(x, y, order = 3, errors = None, returnErrors = True):
	coefs, C = polynomialFit(x, y, order, errors, returnErrors = True)
	#print coefs
	#print C
	"""
	http://www.itl.nist.gov/div898/handbook/mpc/section5/mpc55.htm
	f = ax^2 + bx + c
	min = -b/a2
	
	sigma_min = sqrt((df/da * sigma_a)^2 + (df/db * sigma_b)^2 + (2.0 * sigma_a * sigma_b * cov(a, b)))
		= sqrt(t1 + t2 * t3)
		
	t1 = (df/da * sigma_a)^2
	t1 = (b/(2*a*a) * sigma_a)^2
	
	t2 = (df/db * sigma_b) ^2
	t2 = (-1.0 / (2*a) * sigma_b)
	
	t3 = (df/da * df/db * cov(a, b))
	t3 = (b/(2*a*a) * -1.0 / (2*a) * cov(a, b))
	t3 = (-b / (4 * a^3) * cov(a, b))
	"""
	
	a = coefs[2]
	b = coefs[1]
	var_a = C.item(8)
	var_b = C.item(4)
	covar = C.item(7)
	
	#print coefs
	#print C
	#print a, b, var_a, var_b, covar
	
	result = -b / (2.0 * a)
	
	#pylab.plot(x, y); pylab.plot([result], result*result*coefs[2] + result*coefs[1] + coefs[0], 'ro'); pylab.show()
	
	if not returnErrors:
		return result
	
	#calculate uncertainty
	t1 = ((b / (2.0 * a * a)) ** 2.0) * var_a
	t2 = ((2.0 * a) ** -2.0) * var_b
	t3 = 2.0 * (-b / (4*a*a*a) * covar)
	
	#print t1, t2 ,t3
	
	uncertainty = math.sqrt(t1 + t2 + t3)
	
	return result, uncertainty
	
def testFittingAndInterpolation():	
	x = [0, 1, 2, 3, 5]
	y = [3, 4, 7, 14, 29]
	errors = [1.0, 1.0, 1.0, 1.0, 1.0]
	order = 3
	coefs, C = polynomialFit(x, y, order, errors, returnErrors = True)
	
	#print coefs
	#print C
	
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
		errs = C.dot(Xi.transpose())
		print errs
		
		err = math.sqrt(errs.transpose().dot(errs).sum())
		#print err
		#print errs
		#err = math.sqrt(sum(map(lambda x: x*x, errs)))
		yis.append(err)
	
	axis2.plot(xis, yis, 'red')
	#pylab.show()
	
	pylab.show()
	
def testPolynomialMinFinding():	
	x = [0, 1, 2, 3, 5]
	y = [xi*xi+14.0*xi + 3.0 + random() for xi in x]
	errors = [0.001] * len(x)
	order = 3
	coefs, C = polynomialFit(x, y, order, errors, returnErrors = True)
	
	minX, unc = polynomialFindMinimum(x, y, order, errors, True)
	print 'min: %f +/- %f' % (minX, unc)
	
	xp = numpy.linspace(-5, 5, 100)
	p = numpy.poly1d(coefs[::-1])
	yp = p(xp)
	
	sigmaLevel = 1.0
	xp2 = numpy.linspace(minX-unc * sigmaLevel, minX + unc*sigmaLevel, 20)
	yp2 = p(xp2)
	
	pylab.plot(x, y, '-o')
	pylab.plot(xp, yp, '-')
	pylab.plot(xp2, yp2, 'red')
	pylab.plot(minX, p(minX), 'ro')
	pylab.grid(True)
	pylab.show()
	
def scaleTestMinFinding():
	xs = range(10)
	distances = []
	noise = 3.5
	n = 1000000
	for i in range(n):
		a = random()
		b = random()
		c = random()
		ys = [x*x*a + x*b + c + random() * noise for x in xs]
		
		#print a, b, c, polynomialFit(xs, ys)[::-1]
		minExp, unc = polynomialFindMinimum(xs, ys, returnErrors = True)
		minCalc = -b/(2.0*a)
		dist = (minCalc - minExp) / unc
		#print minCalc, minExp, unc, dist
		distances.append(dist)
		
	print 'mean: %f' % stats.mean(distances)
	print 'stdDev: %f' % stats.stdDev(distances)
	for sigma in [1, 2, 3]:
		print 'With %d sigma: %f%%' % (sigma, 100.0 * sum([int(abs(d) < sigma) for d in distances]) / n)
	
	pylab.hist(distances, bins = 50, range = (-5, 5))
	pylab.show()
	
def testSkewed():
	positions = []
	errors = []
	
	xs = range(10)
	distances = []
	noise = 3.5
	n = 10000
	for i in range(n):
		a = random()
		b = random()
		c = random()
		ys = [x*x*a + x*b + c + random() * noise for x in xs]
		
		#print a, b, c, polynomialFit(xs, ys)[::-1]
		minExp, unc = polynomialFindMinimum(xs, ys, returnErrors = True)
		minCalc = -b/(2.0*a)
		dist = (minCalc - minExp)
		positions.append(minCalc)
		errors.append(minExp)
		
	pylab.plot(positions, errors, 'o')
	pylab.show()
	
def compareToLinear():
	xs = [0, 1, 2, 3, 4, 5]
	ys = [y * 100.0 for y in [1, 3, 5, 7, 9, 11]]
	
	coefs, C = polynomialFit(xs, ys, 2, returnErrors = True)
	print coefs
	print C
	
	print stats.lineOfBestFit(xs, ys, returnErrors = True)
	
if __name__ == "__main__":
	#testFittingAndInterpolation()
	#scaleTestMinFinding()
	#testSkewed()
	#testPolynomialMinFinding()
	compareToLinear()