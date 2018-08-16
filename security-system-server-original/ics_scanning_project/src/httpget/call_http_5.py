# version 1.0
# function : divide the file into any piece, and call any http-progress you want
# preconditon : the dir which contain .txt in format "IP\t\tPort"
# created : 16/11/29
# LastModified : 16/11/29
# author : LQY

import os
import platform
import shutil
from threading import *
import time

sep = '\\' if platform.system() == 'Windows' else '/'

def new_dir(filename, pre) :
    f_split = filename.split(sep)
    new_fold = ''
    for i in range(len(f_split)) :
        if i < len(f_split) - 1 : 
            new_fold += f_split[i] + sep
        elif i == len(f_split) - 1 :
            new_fold += pre + f_split[i]
    No = 1                    # prevent same dir, add _No to the end of the dir
    while(os.path.exists(new_fold)) :
        sp_new_fold = (new_fold.split(sep)[-1]).split('_')
        if( len(sp_new_fold) > 1 and sp_new_fold[-1].isdigit() ) :
            ldigit = len(sp_new_fold[-1])
            No = int(sp_new_fold[-1]) + 1
            new_fold = new_fold[0:-ldigit] + str(No)
        else :
            new_fold = new_fold + '_1'
    os.mkdir(new_fold)
    return new_fold

def getDirAllFileList(Dir) :
    dir_list = []
    for root,dirs,files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root,file))
    return dir_list

def err(ss):
    print(ss)
    exit(0)

def ThreadRun(dirname, ThreadN, out_path) :
    os.system("./httpget -n " + dirname + sep + " -t " + str(ThreadN) + " -f " + out_path + sep)

in_path = input("input your in_path:\n")
if(not os.path.isdir(in_path)) :
    err("Wrong in path or it's not dir!\n")
PNumber = int(input("input the number of the progress:\n"))
ThreadN = int(input("input the thread number in each progress:\n"))
FileList = getDirAllFileList(in_path)
DivideList = []
baseN = int( len(FileList) / PNumber )
leftN = int( len(FileList) % PNumber )
begin = 0
end = 0
for eachP in range(PNumber) :
    eachL = []
    end = begin + baseN
    if(eachP < leftN) :
        end += 1
    for i in range(begin,end) :
        eachL.append(FileList[i])
    begin = end
    DivideList.append(eachL)

out_path = new_dir(in_path, "R3_")
divide_path = new_dir(in_path, "Div_")
ThreadList = []
start_time = int(time.time())
for i in range(PNumber) :
    dirname = divide_path + sep + str(i) # save the divided ip-port
    os.mkdir(dirname)
    #os.mkdir(dirname + sep + "result")
    for ef in DivideList[i] :
        shutil.copy(ef, dirname)
        f_tmp = open(out_path + sep + os.path.basename(ef), "w")
        f_tmp.close()
    NewThread = Thread(target = ThreadRun, args = ( dirname, ThreadN, out_path, ))
    ThreadList.append(NewThread)
    NewThread.start()
for t in ThreadList :
    t.join()
end_time = int(time.time())
f_out = open(out_path + sep + "Total.txt", "w")
f_out.write("Time used : " + str(end_time - start_time))
    
    
