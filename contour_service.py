#!/usr/bin/env python
__version__ = '.01'
__author__ = 'Laird Foret (laird@isotope11.com)'
__copyright__ = '(C) 2015. GNU GPL 3.'

"""
Listens on TCP port for image file. Once received it returns image of contours of original image
"""

import threading
import socket
import cv2
import sys
import numpy as np
import time
import imghdr


class ImageReceiver ( threading.Thread ):
	def __init__( self, IP, data_port ):
		threading.Thread.__init__( self )
		self.IP = IP
		if self.IP == None: self.IP = "" #accept connection from any IP
		self.data_port = data_port

	def run(self):
		self.process()

	def bindmsock( self ):
		self.msock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.msock.bind((self.IP, self.data_port))
		self.msock.listen(2)
		#self.msock.settimeout(2)
		print >> sys.stderr, '[ImageReceiver] Listening on port ', self.data_port

	def acceptmsock( self ):
		self.mconn, self.maddr = self.msock.accept()
		print >> sys.stderr, '[ImageReceiver] Got connection from', self.maddr

	def transfer( self ):
		print >> sys.stderr, '[ImageReceiver] Starting media transfer' # for "%s"' % self.filename
		f = open('temp_image_file',"wb")
		total_data = []
		while 1:
			data = self.mconn.recv(1024)
			total_data.append(data)
			if not data: break
			f.write(data)
		f.close()
		print >> sys.stderr, total_data
		print >> sys.stderr, '[ImageReceiver] data received:', len(total_data)
		print >> sys.stderr, "[ImageReceiver] image type:", imghdr.what('temp_image_file')
		self.get_contour()
	
	def get_contour( self ):
		#read image file
		img = cv2.imread('temp_image_file')	
		#resize image
		dim = (640,480)
		resized_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
		print >> sys.stderr, "[ImageReceiver] resized image to:", dim
		#apply canny 
		edges = cv2.Canny(resized_img,10,100)
		#edges = cv2.cvtColor(resized_img,cv2.COLOR_BGR2GRAY)
		#BLUR THE IMAGE a bit
		blurr = (5,5)
		edges = cv2.blur(edges,blurr)
		print >> sys.stderr, "[ImageReceiver] blurred image:", blurr
		#find contours
		contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		print >> sys.stderr, "[ImageReceiver] Contours found:", len(contours)
		#import inspect
		#print >> sys.stderr, (inspect.getsourcefile(enumerate))
		#get areas of contours and sort them from greatest to smallest
		areaArray= []
		for i, c in enumerate(contours):
			area = cv2.contourArea(c)
			areaArray.append(area)
		#first sort the array by area
		sorted_areas = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)

		#find the nth largest contour [n-1][1], in this case 2
		#in this case return largest
		item_contour = sorted_areas[0][1]

		#create a blank image
		contour_image = np.zeros((dim[1], dim[0], 3), np.uint8)
		#draw contour on blank image
		cv2.drawContours(contour_image, [item_contour], -1, (0, 0, 255), 3)

		#return contour image
		#return contour_image

		#for now just save contour image
		cv2.imwrite('contour_image.bmp', contour_image)
		print >> sys.stderr, "[ImageReceiver] saved contour image: 'contour_image.bmp'"

	def close( self ):
		try:
			self.mconn.close()
			self.msock.close()
			print >> sys.stderr, '[Media] Sockets closed'
		except:
			print >> sys.stderr, "[Media] Sockets not closed"
			time.sleep(.1)
			pass

	def process( self ):
		while 1:
			self.bindmsock()
			#time.sleep(1)
			self.acceptmsock()
			#time.sleep(1)
			self.transfer()
			#time.sleep(1)
			self.close()
			time.sleep(.5)
		    #except:
		    #    print "file xfer failed"
		    #    self.close()
		    #    pass

def start_listening(ip, port):
	s = ImageReceiver(ip, port)
	#line below stops thread when main program stops
	s.daemon = True
	s.start()

if __name__ == '__main__':

	IP = "" #accept from any IP
	PORT = 12345

	start_listening(IP,PORT)
	while 1:
		time.sleep(1)

	
	
	
