import cv2
import pickle
import numpy as np
import pyautogui as gui

with open("range.pickle", "rb") as f:
    t = pickle.load(f)
cam = cv2.VideoCapture(0)
hsv_lower = np.array([t[0], t[1], t[2]])
hsv_upper = np.array([t[3], t[4], t[5]])
width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)	# width of video captured by the webcam
height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)	# height of the video captured by the webcam
max_keys_in_a_row = 10
key_width = int(width/max_keys_in_a_row)	# width of one key. width is divided by 10 as the max number of keys in a single row is 10.


def get_keys():
	# this function is used to design the keyboard

	row1_key_width = key_width * 10			# width of first row of keys
	row2_key_width = key_width * 9			# width of second row
	row3_key_width = key_width * 7			# width of third row
	row4_key_width = key_width * 5			# width of spacebar
	row_keys = []							# stores the keys along with its 2 corner coordinates and the center coordinate

	# for the first row
	x1, y1 = 0, int((height - key_width * 4) / 2)	# 4 is due to the fact that we will have 4 rows. y1 is set such that the whole keyboard has equal margin on both top and bottom
	x2, y2 = key_width + x1, key_width + y1
	c1, c2, c3, c4 = x1, y1, x2, y2					# copying x1, x2, y1 and y2
	c = 0
	keys = "qwertyuiop"
	for i in range(len(keys)):
		row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
		x1 += key_width
		x2 += key_width
		c += 1
	x1, y1, x2, y2 = c1, c2, c3, c4					# copying back from c1, c2, c3 and c4

	# for second row
	x1, y1 = int((row1_key_width - row2_key_width) / 2) + x1, y1 + key_width   # x1 is set such that it leaves equal margin on both left and right side
	x2, y2 = key_width + x1, key_width + y1
	c1, c2, c3, c4 = x1, y1, x2, y2	
	c = 0
	keys = "asdfghjkl"
	for i in range(len(keys)):
		row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
		x1 += key_width
		x2 += key_width
		c += 1
	x1, y1, x2, y2 = c1, c2, c3, c4

	# for third row
	x1, y1 = int((row2_key_width - row3_key_width) / 2) + x1, y1 + key_width
	x2, y2 = key_width + x1, key_width + y1	
	c1, c2, c3, c4 = x1, y1, x2, y2	
	c = 0
	keys = "zxcvbnm"
	for i in range(len(keys)):
		row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
		x1 += key_width
		x2 += key_width
		c += 1
	x1, y1, x2, y2 = c1, c2, c3, c4

	# for the space bar
	x1, y1 = int((row3_key_width - row4_key_width) / 2) + x1, y1 + key_width
	x2, y2 = 5 * key_width + x1, key_width + y1	
	c1, c2, c3, c4 = x1, y1, x2, y2	
	c = 0
	keys = " "
	for i in range(len(keys)):
		row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
		x1 += key_width
		x2 += key_width
		c += 1
	x1, y1, x2, y2 = c1, c2, c3, c4

	return row_keys


def do_keypress(img, center, row_keys_points):
	# this fuction presses a key and marks the pressed key with blue color
	for row in row_keys_points:
		arr1 = list(np.int0(np.array(center) >= np.array(row[1])))			# center of the contour has greater value than the top left corner point of a key 
		arr2 = list(np.int0(np.array(center) <= np.array(row[2])))			# center of the contour has less value than the bottom right corner point of a key 
		if arr1 == [1, 1] and arr2 == [1, 1]:
			gui.press(row[0])
			cv2.fillConvexPoly(img, np.array([np.array(row[1]), np.array([row[1][0], row[2][1]]), np.array(row[2]), np.array([row[2][0], row[1][1]])]), (255, 0, 0))
	return img


def main():
	row_keys_points = get_keys()
	new_area, old_area = 0, 0
	c, c2 = 0, 0									# c stores the number of iterations for calculating the difference b/w present area and previous area
													# c2 stores the number of iterations for calculating the difference b/w present center and previous center
	flag_keypress = False							# if a key is pressed then this flag is True
	while True:
		img = cam.read()[1]
		img = cv2.flip(img, 1)
		imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(imgHSV, hsv_lower, hsv_upper)
		blur = cv2.medianBlur(mask, 15)
		blur = cv2.GaussianBlur(blur , (5,5), 0)
		thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
		contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[1]

		if len(contours) > 0:
			cnt = max(contours, key = cv2.contourArea)
			
			if cv2.contourArea(cnt) > 350:
				# draw a rectangle and a center 
				rect = cv2.minAreaRect(cnt)
				center = list(rect[0])
				box = cv2.boxPoints(rect)
				box = np.int0(box)
				cv2.circle(img, tuple(np.int0(center)), 2, (0, 255, 0), 2)
				cv2.drawContours(img,[box],0,(0,0,255),2)
				
				# calculation of difference of area and center
				new_area = cv2.contourArea(cnt)
				new_center = np.int0(center)
				if c == 0:
					old_area = new_area
				c += 1
				diff_area = 0
				if c > 3:								# after every 3rd iteration difference of area is calculated
					diff_area = new_area - old_area
					c = 0
				if c2 == 0:
					old_center = new_center
				c2 += 1
				diff_center = np.array([0, 0])
				if c2 > 5:								# after every 5th iteration difference of center is claculated
					diff_center = new_center - old_center
					c2 = 0
				
				# setting some thresholds
				center_threshold = 10
				area_threshold = 200
				if abs(diff_center[0]) < center_threshold or abs(diff_center[1]) < center_threshold:
					print(diff_area)
					if diff_area > area_threshold and flag_keypress == False:
						img = do_keypress(img, new_center, row_keys_points)
						flag_keypress = True
					elif diff_area < -(area_threshold) and flag_keypress == True:
						flag_keypress = False
			else:
				flag_keypress = False
		else:
			flag_keypress = False

		# displaying the keyboard
		c1 = 0
		for key in row_keys_points:
			cv2.putText(img, key[0], key[3], cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
			cv2.rectangle(img, key[1], key[2], (0, 255, 0), thickness = 2)
			c1 += 1

		cv2.imshow("img", img)
		
		if cv2.waitKey(1) == ord('q'):
			break

	cam.release()
	cv2.destroyAllWindows()

main()