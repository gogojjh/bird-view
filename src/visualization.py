#!/usr/bin/env python

# Python 2/3 compatibility
from __future__ import print_function


import argparse
import numpy as np
import cv2
import video
import os
from time import sleep
import parseTrackletXML as xmlParser


def load_point(file_path):
    f = open(file_path,'r')
    data = f.readlines()
    lines = []
    for line in data:
        l = line.split()
        l = map(float,l)
        change_coo(l)
        lines.append(l)

    return lines

def plot_obj(canvas,tracklet,frame):
    for trac in tracklet:
        if frame >= trac[1] and frame < trac[1]+len(trac[3]):
            coo = trac[3][frame - trac[1]]
            for i in xrange(4):
                cv2.circle(canvas,_change_coo(coo[0,i],coo[1,i]),3,(0,255,0),-1)
                cv2.line(canvas,_change_coo(coo[0,i],coo[1,i]),_change_coo(coo[0,(i+1)%4],coo[1,(i+1)%4]),(0,255,0),2)


def plot_line(canvas,line):
    line = [(line[2*i],line[2*i+1]) for i in xrange(len(line)/2)]
    line = sorted(line, key = lambda a_tuple:a_tuple[1])
    for i in xrange(len(line)-1):
        cv2.line(canvas,line[i],line[i+1],(0,255,0),2)
    cv2.line(canvas,line[-1],(6*line[-1][0]-5*line[-2][0],6*line[-1][1]-5*line[-2][1]),(0,255,0),2)

def change_coo(line):
    for i in xrange(len(line)/2):
        line[2*i+1], line[2*i+2]=_change_coo(line[2*i+1], line[2*i+2])


def _change_coo(x,y):
    return int(200-y*20),int(800-x*20)

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
    args = parser.parse_args()

    base_path = args.kitti_path
    date_path = os.path.join(base_path, args.date)
    drive_path = os.path.join(date_path, args.drive)
    img_path = os.path.join(drive_path, "image_00/data")
    label_path = os.path.join(drive_path, "label_00")
    lane_path = os.path.join(drive_path, "lane")
    lane_r_path = os.path.join(drive_path, "lane_r")

    command_return = os.popen("find " + lane_r_path + " -name \"*.txt\"")
    cr = command_return.read()
    file_list = cr.split()
    file_list = sorted(file_list, key = lambda ele:int(ele[-14:-4]))

    tracklet = xmlParser.example(date_path, args.drive)

    for f_path in file_list:
        frame = int(f_path[-14:-4])

        img_p = os.path.join(img_path, f_path[-14:-4]+".png")
        img = cv2.imread(img_p)
        cv2.imshow('raw', img)

        canvas = np.zeros((800,400,3), dtype="uint8")
        cv2.rectangle(canvas,_change_coo(1.68,0.8),_change_coo(0,-0.8),(0,255,0),3)
        plot_obj(canvas,tracklet,frame)

        line_point = load_point(f_path)
        for line in line_point:
            plot_line(canvas,line[1:])

        cv2.imshow("Canvas",canvas)

        sleep(0.1)
        ch = cv2.waitKey(5)
        if ch == 27:
            break

    cv2.destroyAllWindows()
