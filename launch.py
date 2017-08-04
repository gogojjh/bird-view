#!/usr/bin/env python

# Python 2/3 compatibility
from __future__ import print_function

import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-k", "--kitti_path",
        help="Path to kitti dir.", default = "/media/csg/WD/kitti/data")
    parser.add_argument(
        "-s", "--step",
        help="The step of label", default = 5)
    parser.add_argument(
        "-v", "--visualization",
        help="Display or not.", default = 0)
    args = parser.parse_args()

    base_path = args.kitti_path

    command_return = os.popen("ls " + base_path)
    cr = command_return.read()
    date_list = cr.split()

    for date in date_list:
        date_path = os.path.join(base_path, date)
        command_return = os.popen("find " + date_path + " -maxdepth 1 -name \"*_sync\"")
        cr = command_return.read()
        drive_list = cr.split()
        for drive in drive_list:
            drive = drive.split("/")[-1]
            print(date + " --- " + drive + " --- Start opt!!!")
            res = os.system("python ./src/opt_flow.py -k " + base_path + " -d "
                        + date + " --drive " + drive + " -s " + str(args.step) + " -v " + str(args.visualization))
            assert res == 0, "Sub-process interrupt!!!"
            print(date + " --- " + drive + " --- Start project!!!")
            res = os.system("python ./src/project.py -k " + base_path + " -d "
                        + date + " --drive " + drive)
            assert res == 0, "Sub-process interrupt!!!"
            if int(args.visualization) == 1:
                print(date + " --- " + drive + " --- Start visualization!!!")
                res = os.system("python ./src/visualization.py -k " + base_path + " -d "
                            + date + " --drive " + drive)
                assert res == 0, "Sub-process interrupt!!!"
            print(date + " --- " + drive + " --- DONE")
