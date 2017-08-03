#!/usr/bin/env python

# Python 2/3 compatibility
# from __future__ import print_function

import numpy as np
import os
import argparse

def load_bin(file_path):
    a = np.fromfile(file_path, dtype=np.float32)
    b = a.reshape(-1,4)
    b = [x for x in b if x[0] > 5]
    b = np.array(b)
    return b

def project(velo_points, P_velo_to_img):
    velo_points[:,-1] = 1
    velo_img_raw = velo_points.dot(P_velo_to_img.T)
    velo_img = []
    for point in velo_img_raw:
        x = point[0]/point[2]
        y = point[1]/point[2]
        velo_img.append([x,y])
    return np.array(velo_img)

def find_vel_point(point, velo_img):
    dis = np.array([abs(point[0]-i[0]) + abs(point[1]-i[1]) for i in velo_img])
    return np.argmin(dis)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-k", "--kitti_path",
        help="Path to kitti dir.", default = "/media/csg/WD/kitti/data")
    parser.add_argument(
        "-d", "--date",
        help="The date of the data", default = "2011_09_26")
    parser.add_argument(
        "-dr", "--drive",
        help="The drive of the data", default = "2011_09_26_drive_0086_sync")

    args = parser.parse_args()

    base_path = args.kitti_path
    data_path = os.path.join(base_path, args.date)
    drive_path = os.path.join(data_path, args.drive)
    img_path = os.path.join(drive_path, "image_00/data")
    label_path = os.path.join(drive_path, "label_00")
    lane_path = os.path.join(drive_path, "lane")
    lane_r_path = os.path.join(drive_path, "lane_r")
    os.system("mkdir -p " + lane_r_path)
    velodyne_path = os.path.join(drive_path, "velodyne_points/data")

    calib_path = os.path.join(data_path, "matric.txt")
    P_velo_to_img = np.loadtxt(calib_path)

    command_return = os.popen("find " + lane_path + " -name \"*.txt\"")
    cr = command_return.read()
    file_list = cr.split()

    for f_path in file_list:
        f_r = open(f_path, "r")
        f_w_path = os.path.join(lane_r_path, f_path[-14:])
        f_w = open(f_w_path, "w")
        bin_path = os.path.join(velodyne_path, f_path[-14:-4]+".bin")
        velo_points = load_bin(bin_path)
        velo_img = project(velo_points, P_velo_to_img)

        lines = f_r.readlines()
        for l in lines:
            line_number = int(l[0])
            f_w.write(str(line_number))
            line = np.array(map(int, l.split())[1:]).reshape(-1,2)
            for point in line:
                index = find_vel_point(point, velo_img)
                f_w.write(' ' + str(velo_points[index][0])+ ' '+ str(velo_points[index][1]))
            f_w.write('\n')
