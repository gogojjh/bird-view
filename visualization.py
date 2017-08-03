import numpy as np
import cv2
import video
import os
from time import sleep

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
    
def plot_line(canvas,line):
    line = [(line[2*i],line[2*i+1]) for i in xrange(len(line)/2)]
    line = sorted(line,key=lambda a_tuple:a_tuple[1])
    for i in xrange(len(line)-1):
        cv2.line(canvas,line[i],line[i+1],(0,255,0),2)
    cv2.line(canvas,line[-1],(6*line[-1][0]-5*line[-2][0],6*line[-1][1]-5*line[-2][1]),(0,255,0),2)

def change_coo(line):
    for i in xrange(len(line)/2):
        line[2*i+1], line[2*i+2]=_change_coo(line[2*i+1], line[2*i+2])
        

def _change_coo(x,y):
    return int(200-y*20),int(800-x*20)
       
if __name__ == '__main__':  
    n = 34
    
    while True:
        n = n + 1
        
        img = cv2.imread('./data/' + '0'*(10-len(str(n))) + str(n) +'.png')
        cv2.imshow('raw', img)
        
        canvas = np.zeros((800,400,3), dtype="uint8")
        cv2.rectangle(canvas,_change_coo(1.68,0.8),_change_coo(0,-0.8),(0,255,0),3)
        file_path = './lane_r/' + '0'*(10-len(str(n))) + str(n) +'.txt'
        line_point = load_point(file_path)
        for line in line_point:
            plot_line(canvas,line[1:])
        
        cv2.imshow("Canvas",canvas)
        
        sleep(0.1)
        ch = cv2.waitKey(5)
        if ch == 27:
            break
        
    cv2.destroyAllWindows()

