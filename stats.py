import math

def covariance(lx, ly):
	ux = mean(lx)
	uy = mean(ly)
	
	result = sum([(x - ux) * (y - uy) for x, y in zip(lx, ly)]) / (len(lx)-1)
	return result
	
def variance(l):
	u = mean(l)
	return sum([(i-u)**2.0 for i in l]) / (len(l)-1)
	
def stdDev(l):
	return math.sqrt(variance(l))

def pearson(lx, ly):
	vx = variance(lx)
	vy = variance(ly)
	if vx == 0.0 or vy == 0.0:
		print 'Pearson(): variance is 0, returning 0 as pearson score'
		return 0	#doesn't really make sense
		
	return covariance(lx, ly) / math.sqrt(vx * vy)
	
def mean(l):
	return sum(l) / float(len(l))
	
def lineOfBestFit(lx, ly):
	lx2 = [float(x) * x for x in lx]
	lxy = [float(x) * y for x, y in zip(lx, ly)]
	
	n = float(len(lx))
	sx2 = sum(lx2)
	sxy = sum(lxy)
	sx = sum([float(x) for x in lx])
	sy = sum([float(y) for y in ly])
	
	denom = n * sx2 - sx * sx
	
	yint = (sy * sx2 - sx * sxy) / denom
	slope = float(n * sxy - sx * sy) / denom
	
	return (slope, yint)
	
#fits a set of points to the function 1 - e^(a*x + b)
def exponentialDecayFit(lx, ly):
	logy = [-math.log(1.0 - min(0.995, y)) for y in ly]
	(decay, offset) = lineOfBestFit(lx, logy)
	return (decay, offset)
	
"""#fit based on a line of best fit with the y-intercept forced to pass through group 0
def sigmoidalFit(lx, ly):	

	group0 = [x for x, y in zip(lx, ly) if y == 0.0]
	#used as offset for function
	offset = mean(group0)
	print 'offset: %s' % offset
	#1.01 used to avoid divide by 0 error
	invSigmoidY = [math.log(-1.0 / min(y-1.0, -0.1)) for y in ly]
	
	#find average slope of resulting function
	slopes = [(y-offset) / x for (x, y) in zip(lx, invSigmoidY)]
	slope = mean(slopes)
	
	return (slope, offset)
	
	#print ly
	#print invSigmoidY
	#exit()
	#(scale, offset) = lineOfBestFit(lx, invSigmoidY)
	#return (scale, offset)
"""

#fit based on finding the horizontal shift from group 0, parameter scaling from group 0.5
def sigmoidalFit(lx, ly):
	(group0, group1, group2) = [[x for x, y in zip(lx, ly) if y == output] for output in [0.0, 0.5, 1.0]]
	mean0 = mean(group0)
	mean1 = mean(group1) 
	
	offset = mean0
	#solve for a in f(x) = 0.5 = 1 / (1 + exp(-ax+b)), where b is the y-int, a is mean1
	#scaling = (offset - math.log(1.0 / 0.5 - 1)) / mean1
	scaling = offset / mean1
	
	return (scaling, offset)
	
"""
def sigmoidalInterpolation(input, params):
	print (params[0] * input + params[1]), max((params[0] * input + params[1]), -100)
	return 1.0 / (1.0 + math.exp(max(params[0] * input + params[1], -100)))
"""

def sigmoidalInterpolation(input, params):
	return 1.0 / (1.0 + math.exp(-params[0] * input + params[1]))
	
def lineInterpolation(input, params):
	return params[0] * input + params[1]
	
def exponentialInterpolation(input, params):
	#also require the output to be >=0
	return max(0.0, 1.0 - math.exp(-params[0] * input + params[1]))
	
def logLinearFit(lx, ly):
	logx = [math.log(x) if x> 0 else 1 for x in lx]
	
	(scale, offset) = lineOfBestFit(logx, ly)
	
	return (scale, offset)
	
def logLinearInterpolation(input, params):
	return (math.log(input) if input > 0 else -1) * params[0] + params[1]
	
def Gaussian(x, sigma = 1.0, center = 0):
	return math.exp((x-center)**2 / (2 * sigma**2))
	
if __name__ == "__main__":
	l1 = [0, 1, 2]
	l2 = [2, 4, 9]
	
	print 'variance: %s' % variance(l2)
	print 'covariance: %s ' % covariance(l1, l2)
	print 'pearson: %s' % pearson(l1, l2)
	print 'slope, yint: %s, %s' % lineOfBestFit(l1, l2)
	
	l1 = [1, 2, 3]
	l2 = [3, 2, 1]
	
	print 'covariance: %s' % covariance(l1, l2)
	print 'pearson: %s ' % pearson(l1, l2)