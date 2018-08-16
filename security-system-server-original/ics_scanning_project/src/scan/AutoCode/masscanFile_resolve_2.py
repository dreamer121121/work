#Version 1.0 in python 3.4.4
#to resolve the result file given by a specific format
#format: IP + '\t' + port
#demand: 10000IP/txt, differ the port
#author LQY
#Created 16.9.21
#LastModified 17.5.19

import string
import os
import platform
import sys
import getopt

sep = '\\' if platform.system() == 'Windows' else '/'

def writePID() :
    dirdirname = os.path.dirname(os.path.dirname(__file__))
    f_PID = open(dirdirname + "/important/PID_masscanFile_resolve.txt", "w")
    f_PID.write(str(os.getpid()))
    f_PID.close()
    
def getIPAccToString(arg) : # arg format : IP + '\t' + port + '\n'
    split_arg = arg.split('\t')
    return split_arg[0]

def getPortAccToString(arg) : # arg format : IP + '\t' + port + '\n'
    split_arg = arg.split('\t')
    if len(split_arg) == 1 :
        return '0'
    return split_arg[1][0:-1]

def getAllFileListInDir(Dir) :
    dir_list = []
    for root,dirs,files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root,file))
    return dir_list


# new a fold in filename with special pre 
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

def usageMFS() :
    print("-i : in-file path\n-o : out-file path\n-m : 1 means add port to the end & 0 means not")

# define the initial data
"""
p2filedata = { # 'port' : ['port', 'NO.?', 'the IP number record now']
    '80' : ['80', 1, 0] ,
    '81' : ['81', 1, 0] ,
    '82' : ['82', 1, 0] ,
    '83' : ['83', 1, 0] ,
    '84' : ['84', 1, 0] ,
    '88' : ['88', 1, 0] ,
    '102': ['102', 1, 0] ,
    '443': ['443', 1, 0] ,
    '502': ['502', 1, 0] ,
    '771': ['771', 1, 0] ,
    '789': ['789', 1, 0] ,
    '1200': ['1200', 1, 0] ,
    '1911': ['1911', 1, 0] ,
    '1962': ['1962', 1, 0] ,
    '2123': ['2123', 1, 0] ,
    '2152': ['2152', 1, 0] ,
    '2404': ['2404', 1, 0] ,
    '2455': ['2455', 1, 0] ,
    '3386': ['3386', 1, 0] ,
    '4800': ['4800', 1, 0] ,
    '4911': ['4911', 1, 0] ,
    '5006': ['5006', 1, 0] ,
    '5007': ['5007', 1, 0] ,
    '5094': ['5094', 1, 0] ,
    '8000': ['8000', 1, 0] ,
    '8080': ['8080', 1, 0] ,
    '8081': ['8081', 1, 0] ,
    '8090': ['8090', 1, 0] ,
    '9600': ['9600', 1, 0] ,
    '10001': ['10001', 1, 0] ,
    '17185': ['17185', 1, 0] ,
    '18245': ['18245', 1, 0] ,
    '18246': ['18246', 1, 0] ,
    '20000': ['20000', 1, 0] ,
    '20547': ['20547', 1, 0] ,
    '30718': ['30718', 1, 0] ,
    '34962': ['34962', 1, 0] ,
    '37777': ['37777', 1, 0] ,
    '44818': ['44818', 1, 0] ,
    '47808': ['47808', 1, 0]
}
"""
p2filedata = {}

"""
in_path = input("input your file in dir\n")
out_path = input("input your output dir\n")
flag = 2
while flag not in [0, 1]:
    flag = int(input("Do you want to add port to file? (0/1)"))
ALL_file_list = getAllFileListInDir(in_path)
"""
opts, args = getopt.getopt(sys.argv[1: ], "i:o:m:u:")
flag = 0
for op,value in opts:
    if op == "-i" :
        in_path = value
    elif op == "-o" :
        out_path = value
    elif op == "-m" :
        flag = int(value)
    else :
        usageMFS()
        sys.exit()
writePID()
ALL_file_list = getAllFileListInDir(in_path)

#begin
for eachFile in ALL_file_list :
    F_in = open(eachFile, 'r')
    Line = F_in.readline()
    while Line != '' :
        Port = getPortAccToString(Line)
        IP = getIPAccToString(Line)
        fileNo = p2filedata.get(Port, ['None', -1, -1])[1]
        filecount = p2filedata.get(Port, ['NONE', -1, -1])[2]
        if filecount < 0 :
            #do not have this port
            p2filedata[Port] = [Port, 1, 0]
            fileNo = 1
            filecount = 0
        if filecount >= 10000 : # file overload 
            p2filedata[Port][1] = p2filedata[Port][1] + 1
            p2filedata[Port][2] = 0
        filename = Port + '_' + str(fileNo) + '.txt'
        F_out = open(out_path + sep + filename, 'a')
        if flag == 1 :
            F_out.write(IP + '\t\t' + Port + '\n')
        else :
            F_out.write(IP + '\n')
        F_out.close()
        p2filedata[Port][2] = p2filedata[Port][2] + 1
        Line = F_in.readline()
    F_in.close()

f_out = open(new_dir(in_path, "TOTAL_") + sep + "TOTAL.txt", "w")
print(p2filedata)
f_out.write("Port\t\tFileNumber\t\tTotal\n")
for item in p2filedata :
    fno = p2filedata.get(item, 'NONE')[1]
    last = p2filedata.get(item, 'NONE')[2]
    f_out.write(item + '\t\t' + str(fno) + '\t\t' + str((fno - 1) * 10000 + last) + "\n")
ALL_IP_NUM = 0
for i in p2filedata :
	ALL_IP_NUM = ALL_IP_NUM + (p2filedata.get(i,'NONE')[1] - 1) *10000 + p2filedata.get(i,'NONE')[2]

print("\nALL_IP_NUM is : " + str(ALL_IP_NUM))
f_out.write("\nALL_IP_NUM is : " + str(ALL_IP_NUM) + "\n")
f_out.close()
