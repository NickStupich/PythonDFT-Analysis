import math
from matplotlib import pylab
from random import random

sps = 768
window = 128

def generateTone(frequency, amplitude = 1.0, func = math.sin, offset = 0.0, noiseAmplitude = 0.0):
	result = [amplitude * func(frequency * (x + offset) * 2.0 * math.pi / sps) + (random() - 0.5) * noiseAmplitude for x in range(window)]
	return result
	
def matchQuality(signal, frequency):
	test1 = generateTone(frequency, func = math.sin)
	test2 = generateTone(frequency, func = math.cos)
	
	products1 = []
	products2 = []
	
	for i in range(len(signal)):
		p1 = signal[i] * test1[i]
		p2 = signal[i] * test2[i]
		
		products1.append(p1)
		products2.append(p2)
		
	#powers = [p1 + p2 for p1, p2 in zip(products1, products2)]
	#result = sum(powers)
	
	result = sum(products1)**2.0 + sum(products2)**2.0
	
	return result
	
if __name__ == "__main__":
	
	if 0:
		signal = generateTone(60.0)
		print matchQuality(signal, 60.0)
	elif 1:
		signal = generateTone(60.0)
		freqs = [(x/100.0) for x in range(1000, 12000)]
		matches = [matchQuality(signal, f) for f in freqs]
		i = matches.index(max(matches))
		print zip(freqs[i-5:i+5], matches[i-5:i+5])
		noiseFrequency = freqs[matches.index(max(matches))]
		print noiseFrequency
		pylab.plot(freqs, matches)
		pylab.grid(True)
		pylab.show()
	else:
		freqs = [(x/10.0) for x in range(500, 700)]
		offsets = [x/10.0 for x in range(-10, 10)]
		allMatches = []
		
		for offset in offsets:
			signal = generateTone(60.0, offset)
			freqs = [(x/10.0) for x in range(500, 700)]
			matches = [matchQuality(signal, f) for f in freqs]
			
			pylab.plot(freqs, matches)
		pylab.grid(True)
		pylab.show()
