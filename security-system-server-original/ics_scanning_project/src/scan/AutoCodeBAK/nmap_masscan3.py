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
import getopt
import sys

def writePID() :
    dirdirname = os.path.dirname(os.path.dirname(__file__))
    f_PID = open(dirdirname + "/important/PID_nmap_masscan.txt", "w")
    f_PID.write(str(os.getpid()))
    f_PID.close()

def getDirAllFileList(Dir) :
    dir_list = []
    for root,dirs,files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root,file))
    return dir_list

def ThreadRun(masscan, iLFile, Port, outFile, whichPort) :
    """
    udp = ['9600', '137', '161', '5006']
    both = ['9600']
    if Port in both :
        os.system(masscan + ' -sS -iL ' + iLFile + ' -p ' + Port + ' -oG ' + outFile)
        os.system(masscan + ' -sU -iL ' + iLFile + ' -p ' + Port + ' -oG ' + outFile)
    elif Port not in udp:
        os.system(masscan + ' -sS -iL ' + iLFile + ' -p ' + Port + ' -oG ' + outFile)
    elif Port in udp :
        os.system(masscan + ' -sU -iL ' + iLFile + ' -p ' + Port + ' -oG ' + outFile)
    """
    if not whichPort :
        PortTCP, PortUDP = Port.split(";")
        os.system(masscan + ' -sS -iL ' + iLFile + ' -Pn -p ' + PortTCP + ' -oG ' + outFile + ' --host-timeout 180')
        #os.system(masscan + ' -sU -iL ' + iLFile + ' -p ' + PortUDP + ' -oG ' + outFile[:-4] + "_U.txt")
    else :
        os.system(masscan + ' -sS -iL ' + iLFile + ' -Pn -p ' + Port + ' -oG ' + outFile + ' --host-timeout 180')

def usageNM():
    print("-i : in-file path\n-o : out-file path\n-m : 1 means http & 0 means not")
"""
in_file = input("input your iL-file dir\n")
masscan = input("input your tools like nmap or masscan\n")
out_file =input("input your output dirPath\n")
whichPort = int(input("HTTP or not(0/1)"))
"""
opts, args = getopt.getopt(sys.argv[1: ], "i:o:m:u:")
in_file = ""
out_file = ""
whichPort = ""
masscan = "nmap"
for op, value in opts:
    if op == "-i" :
        in_file = value
    elif op == "-o" :
        out_file = value
    elif op == "-m" :
        whichPort = int(value)
    else:
        usageNM()
        sys.exit()
writePID()
ALL_IL = getDirAllFileList(in_file)
if(len(in_file) > 256) :
    print("too much thread!\n")
    exit(0)
ThreadList = []
Port1 = "80,443,8080,21,81,8000,161,82,1434,8081,83,88,8090"
Port2 = "80,102,445,502,789,1200,1911,1962,2404,2222,2455,4800,5007,8080,10001,20000,20547,44818,47808;137,161,5006"
Port3 = "21,80,81,82,83,102,161,443,445,502,789,1200,1434,1911,1962,2404,2222,2455,4800,5007,8000,8080,8081,8090,10001,20000,20547,44818,47808;137,161,5006"
Port = ""
if whichPort :
    Port = Port1
else :
    Port = Port3
for each_il in ALL_IL :
    NewThread = Thread(target = ThreadRun, args = (masscan, each_il, Port, out_file + "/"+ os.path.basename(each_il), whichPort ))
    ThreadList.append(NewThread)
    NewThread.start()
