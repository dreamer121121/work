#Version 7.0
#precondition : already have resolve the 'IP\t\tPort' file 
#function : analize IP & Port according to the file with nmap.exe
#introduction : in this version, you can set any number of thread to do the job, each thread will open the 'IP\t\tPort' file to analize all IP included 
#incompleteness : 
#author : LQY
#Created 16.10.7
#LastModified 17.4.26

import os
from threading import *
import time
import platform

# to suit windows and linux file path
sep = '\\' if platform.system() == 'Windows' else '/'

# to differ the TCP and UDP
def TCPorUDP(port) :
    if(port == "5006") :
        return " -sU "
    return ""

# Thread_ID must less than Thread_Number

def ThreadRun(Each_Thread_File_List, masscan, nse, AN_dir, Thread_ID, Thread_Number) :
    Thread_Counter = -1
    for Thread_File in Each_Thread_File_List :
        Thread_Counter = Thread_Counter + 1
        File_No = int(Thread_ID) + int(Thread_Counter) * int(Thread_Number) # for different file in the same threads
        Thread_File_Name = os.path.basename(Thread_File)
        Port = Thread_File_Name.split('_')[0]
        os.system(masscan + ' -p ' + Port + TCPorUDP(Port)  + ' -Pn --script ' + nse + ' -iL ' + Thread_File + ' -oN ' + AN_dir + sep + Thread_File_Name)
    
        
# new a fold in filename with special pre.3
# precondition : file is dir 
def new_dir(filename, pre) :
    f_split = filename.split(sep)
    del(f_split[0])
    new_fold = sep
    for i in range(len(f_split)) :
        if i < len(f_split) - 1 : 
            new_fold += f_split[i] + sep
        elif i == len(f_split) - 1 :
            new_fold += pre + f_split[i]
    No = 1
    while(os.path.exists(new_fold)) :
        new_fold = new_fold + '_' + str(No)
        No = No + 1
    os.mkdir(new_fold)
    return new_fold


def add_pre(filename, pre) :
    f_split = filename.split(sep)
    del(f_split[0])
    new_file = sep
    for i in range(len(f_split)) :
        if i < len(f_split) - 1 :
            new_file += f_split[i] + sep
        elif i == len(f_split) - 1 :
            new_file += pre + f_split[i]
    return new_file

# return all file in Dir or Dir/Dir etc.
def getDirAllFileList(Dir) :
    dir_list = []
    for root,dirs,files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root,file))
    return dir_list

# 0.input-------------------------------------------------------------------------------------------------------

in_path = input("input your file dirPath\n")
masscan = input("input your masscan dirPath\n")
nse = input("input your nse\n")
# ThreadNum = int(input("input your thread number\n"))
AN_dir = input("input your output file path\n")

if(os.path.isfile(in_path)) :
    print("Sorry, We need dir path !")
    exit()
ALL_File_List = getDirAllFileList(in_path)
ThreadNum = len(ALL_File_List)
# 1.divide the ALL_File_List into int(threadNumber) part-----------------------------------------------------------
    # for some reason , the File is not divided by the order of filename
File_Divide_List = []
for ThreadID in range(ThreadNum) :
    Thread_File_List = []
    for FileNo in range(int(len(ALL_File_List) / ThreadNum)) :
                        Thread_File_List.append(ALL_File_List[ThreadNum * FileNo + ThreadID])
    if(ThreadID < int(len(ALL_File_List ) % ThreadNum)) :
        Thread_File_List.append(ALL_File_List[int(len(ALL_File_List) / ThreadNum) * ThreadNum + ThreadID])
    File_Divide_List.append(Thread_File_List)

# 2. build up Threads to run nmap------------------------------------------------------------------------------------
ThreadList = []
for ThreadCount in range(ThreadNum) :
    NewThread = Thread(target = ThreadRun, args = (File_Divide_List[ThreadCount], masscan, nse, AN_dir, ThreadCount, ThreadNum))
    ThreadList.append(NewThread)
    NewThread.start()


    



