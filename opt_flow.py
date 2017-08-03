#!/usr/bin/env python

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2
import video
import os
import xml.etree.ElementTree as ET

my_lane = []

def load_xml(path_to_file):
    tree = ET.parse(path_to_file)
    root = tree.getroot()

    lane = []

    for obj in root.iter('object'):
        for i in obj.iter('name'):
            name =  i.text
        index = -1
        one = [int(name[0])]
        for i in range(len(lane)):
            if lane[0][0] == int(name[0]):
                index = i
                break

        for bndbox in obj.iter('bndbox'):
            if name[1:] == '13':
                if index == -1:
                    one.append([[int(bndbox[0].text), int(bndbox[1].text)], [int(bndbox[2].text), int(bndbox[3].text)]])
                    lane.append(one)
                else:
                    lane[index][1].append([int(bndbox[0].text), int(bndbox[1].text)])
                    lane[index][1].append([int(bndbox[2].text), int(bndbox[3].text)])
            else:
                if index == -1:
                    one.append([[int(bndbox[2].text), int(bndbox[1].text)], [int(bndbox[0].text), int(bndbox[3].text)]])
                    lane.append(one)
                else:
                    lane[index][1].append([int(bndbox[2].text), int(bndbox[1].text)])
                    lane[index][1].append([int(bndbox[0].text), int(bndbox[3].text)])

    return lane

def draw_flow(img, flow, n, my_lane, step=16):
    y = []
    x = []
    for lane in my_lane:
        for point in lane[1]:
            if point[1]>=0 and point[1]<=375:
                y.append(point[1])
                x.append(point[0])
    
    #h, w = img.shape[:2]
    #y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    fx, fy = flow[y,x].T
    
    index = 0
    for lane in my_lane:
        for point in lane[1]:
            if point[1]>=0 and point[1]<=375:
                point[0] += int(fx[index])
                point[1] += int(fy[index])
                index += 1
            
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 3, (0, 255, 0), -1)
    return vis
    
def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:,:,0], flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = 255
    hsv[...,2] = np.minimum(v*4, 255)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr

def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return res

if __name__ == '__main__':
    import sys
    n = 35
    prev = cv2.imread('./img/'+ '0'*(10-len(str(n))) + str(n) +'.png')
    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    show_hsv = False
    show_glitch = False
    cur_glitch = prev.copy()

    while True:
        n = n + 1
        img = cv2.imread('./img/'+ '0'*(10-len(str(n))) + str(n) +'.png')
        
        if n%5 == 1:
            curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
            xmls_path = os.path.join(curr_path, '../label_00')
            path_to_file = os.path.join(xmls_path, '0'*(10-len(str(n-1))) + str(n-1)+".xml")
            my_lane = load_xml(path_to_file)
              
        # print (my_lane)
        os.system("mkdir lane -p")
        f = open('./lane/'+ '0'*(10-len(str(n-1))) + str(n-1) +'.txt', 'w')
        for i in my_lane:
            f.write(str(i[0])+'\t')
            for point in i[1]:
                f.write(str(point[0])+'\t'+str(point[1])+'\t')
            f.write('\n')
            
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevgray = gray

        draw_flow(gray, flow, n, my_lane)
        """
        cv2.imshow('flow', draw_flow(gray, flow, n, my_lane))

        ch = cv2.waitKey(5)
        if ch == 27:
            break
        if ch == ord('1'):
            show_hsv = not show_hsv
            print('HSV flow visualization is', ['off', 'on'][show_hsv])
        if ch == ord('2'):
            show_glitch = not show_glitch
            if show_glitch:
                cur_glitch = img.copy()
            print('glitch is', ['off', 'on'][show_glitch])
        """
            
        
    cv2.destroyAllWindows()
    
