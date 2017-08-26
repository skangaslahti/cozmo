import sys
import time
import numpy as np
import cozmo
import asyncio
from matplotlib import pyplot as plt
import cv2

#@cozmo.annotate.annotator
def run (sdk_conn):
    time.sleep(5)
    robot = sdk_conn.wait_for_robot(timeout = 10)
    robot.set_robot_volume(0.0)
    
    head_state = cozmo.action.ACTION_FAILED
    #while (head_state != cozmo.action.ACTION_SUCCEEDED):
    head_state = robot.set_head_angle(cozmo.robot.MIN_HEAD_ANGLE).wait_for_completed()
    
    lift_state = cozmo.action.ACTION_FAILED
    #while (lift_state != cozmo.action.ACTION_SUCCEEDED):
    lift_state = robot.set_lift_height(1.0,in_parallel = True).wait_for_completed()
    
    while (True):
        robot.camera.image_stream_enabled = True
        print ("Image Stream Enabled")
        frame = robot.world.latest_image
        print (frame)
        
        robot.set_head_angle(cozmo.robot.MIN_HEAD_ANGLE).wait_for_completed()
        
        raw = frame.raw_image
        
        pix_mat = np.array(raw.getdata(),dtype='uint8').reshape(raw.size[0], raw.size[1],3)
        
        cropped_img = pix_mat[0:80, 80:240]
        
        gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        
        blur = cv2.GaussianBlur(gray,(5,5),0)
        
        thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
        #(ret, thresh) = cv2.threshold(blur,20,255,cv2.THRESH_BINARY_INV)
        
        print (thresh.dtype)
        
        image, contours, hierarchy = cv2.findContours(thresh,1,cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            
            M = cv2.moments(c)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            
            print (cx, cy)
            
            x_mm = 0.0
            y_mm = 34.3
            
            if cx > 85:
                x_mm = (y_mm * (cx-80))/cy
            elif cx < 75:
                x_mm = (y_mm * (80-cx))/cy
            elif 75 <= cx and cx <= 85:
                x_mm = 0.0
            else:
                print ('Robot off track!')
                return
            
            print ('x_mm:' + str(x_mm))
            
            if x_mm == 0:
                robot.drive_straight(cozmo.util.Distance(distance_mm = y_mm-10), cozmo.util.Speed(speed_mmps = 50)).wait_for_completed()
            else:
                turn_angle = np.arctan(x_mm/y_mm)
                duration = (12 * turn_angle)/(2*np.pi)
                if cx > 85:
                    robot.drive_wheels(0,-50,0,0,duration = duration)
                else:
                    robot.drive_wheels(-50,0,0,0,duration = duration)
                    
            cv2.line(thresh,(cx,0),(cx,720),(255,0,0),1)
            cv2.line(thresh,(0,cy),(1280,cy),(255,0,0),1)
 
            cv2.drawContours(thresh, contours, -1, (0,255,0), 1)
            rgb_img = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
            plt.imshow(rgb_img)
        
            
     #      ''' 
cozmo.run.connect(run)
#cozmo.run_program(annotate, use_viewer=True, force_viewer_on_top=True)
