import urllib2
import re
import time
import sys

def getCurrentFrequency():
	url = "http://www.nationalgrid.com/ngrealtime/realtime/systemdata.aspx"
	text = urllib2.urlopen(url).read()
	m = re.search('(?<=Frequency: )[0-9\.]+', text)
	freq = m.group(0)
	m2 = re.search('(?<=Hz<BR/>)[0-9:]+', text)
	t = m2.group(0)
	return t, freq
	
def saveData(delaySeconds = 60):
	f = open('ukPowerFrequencies.txt', 'a')
	for x in xrange(1000000):	
		sys.stdout.write('\r%s' % x)
		t, freq = getCurrentFrequency()
		f.write('%s\t%s\n' % (t, freq))
		time.sleep(delaySeconds)
		
	f.close()
	
if __name__ == "__main__":
	#print getCurrentFrequency()
	saveData()