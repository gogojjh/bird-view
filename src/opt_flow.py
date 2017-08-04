#!/usr/bin/env python

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2
import video
import os
import xml.etree.ElementTree as ET
import argparse

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
            if lane[i][0] == int(name[0]):
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
            if point[1]>0 and point[1]<375:
                y.append(point[1])
                x.append(point[0])

    #h, w = img.shape[:2]
    #y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    fx, fy = flow[y,x].T

    index = 0
    for lane in my_lane:
        for point in lane[1]:
            if point[1]>0 and point[1]<375:
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-k", "--kitti_path",
        help="Path to kitti dir.", default = "/media/csg/WD/kitti/data")
    parser.add_argument(
        "-d", "--date",
        help="The date of the data", default = "2011_09_26")
    parser.add_argument(
        "--drive",
        help="The drive of the data", default = "2011_09_26_drive_0001_sync")
    parser.add_argument(
        "-s", "--step",
        help="The step of label", default = 5)
    parser.add_argument(
        "-v", "--visualization",
        help="Display or not.", default = 0)
    args = parser.parse_args()

    base_path = args.kitti_path
    date_path = os.path.join(base_path, args.date)
    drive_path = os.path.join(date_path, args.drive)
    img_path = os.path.join(drive_path, "image_00/data")
    label_path = os.path.join(drive_path, "label_00")
    lane_path = os.path.join(drive_path, "lane")
    os.system("mkdir -p " + lane_path)

    break_recovery = 0
    step = int(args.step)

    command_return = os.popen("ls " + label_path + " | sort | awk \'NR==1\'")
    min_n = command_return.read()[:10]
    command_return = os.popen("ls " + label_path + " | sort -r | awk \'NR==1\'")
    max_n = command_return.read()[:10]
    min_frame = int(min_n)
    max_frame = int(max_n)

    n = min_frame
    if n%step == 0:
        path_to_file = os.path.join(label_path, '0'*(10-len(str(n))) + str(n)+".xml")
        my_lane = load_xml(path_to_file)

    _img_path = os.path.join(img_path, '0'*(10-len(str(n))) + str(n) +'.png')
    prev = cv2.imread(_img_path)
    prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    while True:
        n += 1
        if n > max_frame:
            break
        if n%step == 0:
            path_to_file = os.path.join(label_path, '0'*(10-len(str(n))) + str(n)+".xml")
            try:
                my_lane = load_xml(path_to_file)
            except:
                break_recovery = 1
                n += step - 1
                continue

        if break_recovery:
            _img_path = os.path.join(img_path, '0'*(10-len(str(n-1))) + str(n-1) +'.png')
            prev = cv2.imread(_img_path)
            prevgray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

        # print (my_lane)

        lane_txt_path = os.path.join(lane_path, '0'*(10-len(str(n-1))) + str(n-1) +'.txt')
        f = open(lane_txt_path, 'w')
        for i in my_lane:
            f.write(str(i[0])+'\t')
            for point in i[1]:
                f.write(str(point[0])+'\t'+str(point[1])+'\t')
            f.write('\n')

        _img_path = os.path.join(img_path, '0'*(10-len(str(n))) + str(n) +'.png')
        img = cv2.imread(_img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevgray = gray

        draw_flow(gray, flow, n, my_lane)
        if args.visualization == 1:
            cv2.imshow('flow', draw_flow(gray, flow, n, my_lane))

            ch = cv2.waitKey(5)
            if ch == 27:
                break

    cv2.destroyAllWindows()
