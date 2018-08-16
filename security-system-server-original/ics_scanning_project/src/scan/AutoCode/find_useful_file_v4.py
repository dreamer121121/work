import os
import platform
import getopt
import sys
sep = '\\' if platform.system() == 'Windows' else '/'

def writePID() :
    dirdirname = os.path.dirname(os.path.dirname(__file__))
    f_PID = open(dirdirname + "/important/PID_find_useful_file.txt", "w")
    f_PID.write(str(os.getpid()))
    f_PID.close()
    
#from "xx" to "prexx"
def new_dir(filename, pre) :
    f_split = filename.split(sep)
    new_fold = ''
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

def getDirAllFileList(Dir) :
    dir_list = []
    for root,dirs,files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root,file))
    return dir_list


def find_create_useful_file(file, out_path) :
    useful_str = ""
    useful_number = 0
    f_in_file = open(file, "r")
    ALL = f_in_file.read()
    f_in_file.close()
    ALL_IP_AN = ALL.split("\nNmap scan ")
    for each_ip_an in ALL_IP_AN :
        if "ERROR" in each_ip_an or "failed" in each_ip_an or "TIMEOUT" in each_ip_an:
            print("find ERROR!")
            continue
        mark = False
        all_line = each_ip_an.split('\n')
        #if(len(all_line) >= 8) :
        if True :
            for each_line in all_line :
                if(each_line != "" and each_line[0] == '|') :
                    if(each_line[1] == '_') : #nse |_ means end
                        break
                    tmp = each_line.split(": ")
                    if(len(tmp) < 1 or tmp[1] != "ERROR") :
                        mark = True
                        break
        if(mark) :
            useful_str = useful_str + each_ip_an + '--------------------------------------------------\n'
            useful_number = useful_number + 1
    if useful_number == 0 or useful_str == "":
        return useful_number
    f_out_file = open(out_path + sep + os.path.basename(file), "w")
    #f_out_file.write(useful_str + "\n-----------------------\n Useful IP number is : " + str(useful_number) + '\n')
    f_out_file.write("Useful Number Is : " + str(useful_number) + '\n--------------------------------------------------\n' + useful_str)
    f_out_file.close()
    return useful_number

def usageFUF() :
    print("-i : in_file path\n-o : out_file path")
            
all_ip_useful = 0
"""
in_path = input("input your dir to find useful file :\n")
out_path = input("input your out-file path\n")
"""
opts, args = getopt.getopt(sys.argv[1: ], "i:o:u:")
for op, value in opts :
    if op == "-i" :
        in_path = value
    elif op == "-o" :
        out_path = value
    else :
        usageFUF()
        sys.exit()

writePID()
File_List = getDirAllFileList(in_path)
for each_file in File_List :
    all_ip_useful += find_create_useful_file(each_file, out_path)
OUT_FILE = getDirAllFileList(out_path)
"""
for each_file in OUT_FILE :
    f_out = open(each_file, "r")
    tmpstr = f_out.read()
    if tmpstr == "" :
        f_out.close()
        os.remove(each_file)
    else :
        f_out.close()
"""
print("\nAll useful ip number is : " + str(all_ip_useful) + '\n')


