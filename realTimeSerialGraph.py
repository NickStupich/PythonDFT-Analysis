import serial
from matplotlib import pylab
import time
from threading import Thread
import math

_port = "COM4"
_baud = 115200

dataBuf = []
bufLength = 1000

pylab.ion()

class SerialCom(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.ser = serial.Serial(port = _port, baudrate = _baud, timeout = 1)
		
		self.isRunning = True
		
	def run(self):
		while self.isRunning:
			b = self.ser.read(3)
			if b:
			"""MARK:  b[0], b[1], b[2] are the three bytes, encoded as characters.  ord(x) will convert to numerical value from 0-256"""
				val = (ord(b[2])<<0) + (ord(b[1])<<8) + (ord(b[0])<<16)
				dataBuf.append(val)
				
	def Stop(self):	
		self.isRunning = False
				
class GraphUpdates(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.isRunning = True
		
	def run(self):
		self.xs = range(bufLength)
		while len(dataBuf) < bufLength and self.isRunning:
			time.sleep(0.1)
			
		line, = pylab.plot(self.xs, dataBuf[-bufLength:])
		while self.isRunning:
			tempBuf = dataBuf[-bufLength:]
			line.set_ydata(tempBuf)
			pylab.draw()
			
			time.sleep(0.01)
		
	def Stop(self):
		self.isRunning = False
		
if __name__ == "__main__":
	sc = SerialCom()
	gu = GraphUpdates()
	
	sc.start()
	gu.start()
	
	s = raw_input()
	
	sc.Stop()
	gu.Stop()