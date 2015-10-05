
import cv2
import sys
import numpy as np
import time
import imghdr


def get_contour():
		#read image file
		img = cv2.imread('temp_image_file')	
		#resize image
		dim = (640,480)
		resized_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
		print >> sys.stderr, "[ImageReceiver] resized image to:", dim
		#apply canny

		edges = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
		edges = cv2.Canny(edges,40,180)
		
		#ret,edges = cv2.threshold(edges, 127,255,cv2.THRESH_BINARY)
		
		kernel = np.ones((5,5),np.uint8)
		edges = cv2.dilate(edges,kernel,iterations = 2)
		#edges= cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
		edges = cv2.erode(edges,kernel,iterations = 1)
		
		#edges = cv2.adaptiveThreshold(edges, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 					cv2.THRESH_BINARY_INV, 11, 1)
		
		#BLUR THE IMAGE a bit
		blurr = (3,3)
		edges = cv2.blur(edges,blurr)
		cv2.imwrite('blurred_image.jpg', edges)
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
		#contour_image = cv2.erode(edges,kernel,iterations = 1)
		
		#return contour image
		#return contour_image

		#for now just save contour image
		cv2.imwrite('contour_image.bmp', contour_image)
		print >> sys.stderr, "[ImageReceiver] saved contour image: 'contour_image.bmp'"
		return None
		

