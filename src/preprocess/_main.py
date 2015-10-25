#!/usr/bin/env python

import cv2
import numpy as np
import sys

SZ = 120
affine_flags = cv2.WARP_INVERSE_MAP|cv2.INTER_LINEAR

file_name = ""

def morph(img):
	img = cv2.GaussianBlur(src,(5,5),0)
	img = cv2.adaptiveThreshold(img,255,1,1,11,2)
	return img

def roi_op(img,thresh):
	contours,hierarchy = cv2.findContours(img,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	for cnt in contours:
		if cv2.contourArea(cnt)>50:
			[x,y,w,h] = cv2.boundingRect(cnt)
			if  h>70:
				roi = thresh[y:y+h,x:x+w]
				print "ROI shape : ",roi.shape
				# resize roi to 100x100
				roi_100x100 = cv2.resize(roi,(100,100), interpolation = cv2.INTER_CUBIC)
				return roi_100x100

def center(roi_100x100):
	bg = np.zeros((120,120), np.uint8)
	x_offset=y_offset=10
	bg[y_offset:y_offset+roi_100x100.shape[0], x_offset:x_offset+roi_100x100.shape[1]] = roi_100x100
	return bg

def deskew(img):
	m = cv2.moments(img)
	if abs(m['mu02']) < 1e-2:
		return img.copy()
		skew = m['mu11']/m['mu02']
		print "Skew : %f" %(skew)
		M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
		img = cv2.warpAffine(img,M,(SZ, SZ),flags=affine_flags)
		return img

def writeToFile(thresh,centered,deskewed):
	cv2.imwrite(output_path + file_name + "_threshold.png",  thresh)
	cv2.imwrite(output_path + file_name + "_centered.png", centered)
	cv2.imwrite(output_path + file_name + "_deskewed.png", deskewed)

def display(thresh,centered,deskewed):
	cv2.imshow('original',thresh)
	cv2.imshow('centered',centered)
	cv2.imshow('deskewed',deskewed)
	cv2.waitKey(0)

if __name__ == '__main__':
	file_name = sys.argv[1]
	output_path = ""
	src = cv2.imread("../../data/02/" + file_name + ".tiff",0)
	src = cv2.resize(src,(120,120), interpolation = cv2.INTER_CUBIC)

	thresh = morph(src).copy()
	deskewed = deskew(thresh)
	deskewed_copy = deskewed.copy()
	roi = roi_op(deskewed_copy,deskewed).copy()
	centered = center(roi)

	# write to file
	writeToFile(thresh,centered,deskewed)

	# display
	#display(thresh,centered,deskewed)

	cv2.destroyAllWindows()