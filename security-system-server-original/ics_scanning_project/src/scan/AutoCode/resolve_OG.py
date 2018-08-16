import os
import string
import platform
import sys
import getopt

sep = '\\' if platform.system() == 'Windows' else '/'

def writePID() :
    dirdirname = os.path.dirname(os.path.dirname(__file__))
    f_PID = open(dirdirname + "/important/PID_resolve_OG.txt", "w")
    f_PID.write(str(os.getpid()))
    f_PID.close()

def AddAllFileToList(Dir, ALL_File_List) :
    FileNumber = 0
    for root,dirs,files in os.walk(Dir):
        for file in files:
            ALL_File_List.append(os.path.join(root,file))
            FileNumber += 1
    return FileNumber


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

def err(ss) :
    print(ss)
    exit(0)

def usageROG() :
    print("-i : in-file path\n-o : out-file path\n-m : 1 means find open-state & 0 means not")

opts, args = getopt.getopt(sys.argv[1: ], "i:o:m:u:")
for op, value in opts :
    if op == "-i" :
        in_path = value
    elif op == "-o" :
        out_path = value
    elif op == "-m" :
        Flag = int(value)
    else :
        usageROG()
        sys.exit()
writePID()
#in_path = input("input your file in_path\n")
#Flag = int(input("Do you want to find the open-state ip?(1/0)\n"))
if(Flag not in [0, 1]) :
    err("wrong answer!\n")
#out_path = input("input your file out path\n")
FileList = []
if(os.path.isfile(in_path)) :
    err("can't resolve file now!\n")
else :
    AddAllFileToList(in_path, FileList)
TOTAL = 0
if(Flag) :
    for EachFile in FileList :
        f_in = open(EachFile, "r")
        f_out = open(out_path + sep + os.path.basename(EachFile), "w")
        Total = 0
        lines = f_in.readlines()
        f_in.close()
        ll = len(lines)
        if(ll < 4) :
            continue
        Number = int((ll - 2) / 2)
        for i in range(Number) :
            No = i * 2 +  2
            line = lines[No]
            line = line.split("\t")
            if(len(line) < 2) :
                continue
            line = line[1] #Ports: or Timeout
            if "Timeout" in line :
                continue
            line = line.split(" ")
            for j in range(1, len(line)) :
                partline = line[j].split("/")
                if len(partline) < 2 :
                    continue
                if partline[1] == "open" :
                    IP = lines[No].split(" ")[1]
                    Port = partline[0]
                    f_out.write(IP + '\t' + Port + '\n')
                    TOTAL += 1
        f_out.close()
else :
    for EachFile in FileList :
        f_in = open(EachFile, "r")
        f_out = open(out_path + sep + os.path.basename(EachFile), "w")
        Total = 0
        lines = f_in.readlines()
        f_in.close()
        ll = len(lines)
        if(ll < 4) :
            continue
        Number = int((ll - 2) / 2)
        for i in range(Number) :
            No = i * 2 +  2
            line = lines[No]
            line = line.split("\t")
            if(len(line) < 2) :
                continue
            line = line[1]
            if "Timeout" in line :
                continue
            line = line.split(" ")
            for j in range(1, len(line)) :
                partline = line[j].split("/")
                if len(partline) < 2 :
                    continue
                if partline[1] != "closed" :
                    IP = lines[No].spilt(" ")[1]
                    Port = partline[0]
                    f_out.write(IP + '\t' + Port + '\n')
                    TOTAL += 1
        f_out.close()
print("Total number is : " + str(TOTAL))
