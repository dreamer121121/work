#Version 3.0 expecially for Tianjin IP
#precondition :  
#function : PLC-detecte by nmap.exe
#introduction : in this version, you can set any number of thread to do the job
#incompleteness : 
#author : LQY
#Created 16.11.23
#LastModified 17.03.22

import os
from threading import *
import time

def getDirAllFileList(Dir) :
    dir_list = []
    for root,dirs,files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root,file))
    return dir_list

def ThreadRun(masscan, iLFile, Port, outFile) :
    os.system(masscan + ' -sS -iL ' + iLFile + ' -p ' + Port + ' -oG ' + outFile)

in_file = input("input your iL-file dir\n")
masscan = input("input your tools like nmap or masscan\n")
out_file =input("input your output dirPath\n")
whichPort = int(input("HTTP or not(0/1)"))

ALL_IL = getDirAllFileList(in_file)
if(len(in_file) > 256) :
    print("too much thread!\n")
    exit(0)
ThreadList = []
Port1 = "80,443,8080,21,81,8000,161,82,1434,8081,83,88,8090"
Port2 = "102,502,1200,1911,1962,2222,2455,5007,9600,10001,20000,20547,44818,47808"
Port = ""
if whichPort :
    Port = Port1
else :
    Port = Port2
for each_il in ALL_IL :
    NewThread = Thread(target = ThreadRun, args = (masscan, each_il, Port, out_file + "/"+ os.path.basename(each_il) ))
    ThreadList.append(NewThread)
    NewThread.start()
