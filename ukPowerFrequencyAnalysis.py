import stats
from matplotlib import pylab

f = open('ukPowerFrequencies.txt')
frequencies = [float(line.split('\t')[-1]) for line in f]

print '# Points: %s' % len(frequencies)
print 'mean: %s' % stats.mean(frequencies)
print 'stdDev: %s' % stats.stdDev(frequencies)
print 'range: (%s - %s)' % (min(frequencies), max(frequencies))

pylab.hist(frequencies, 50)
pylab.show()