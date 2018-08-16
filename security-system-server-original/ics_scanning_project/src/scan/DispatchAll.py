# Version 1.0 in python 3.4.4
import os
import time
import common.settings as  SETTINGS

dirname = os.path.dirname(__file__)
sep = '/'
PIDFile_DivideIP =  dirname + sep + "important/PID_DivideIP.txt"
PIDFile_find_useful_file = dirname + sep + "important/PID_find_useful_file.txt"
PIDFile_masscan = dirname + sep + "important/PID_masscan.txt"
PIDFile_masscanFile_resolve = dirname + sep + "important/PID_masscanFile_resolve.txt"
PIDFile_nmap_masscan = dirname + sep + "important/PID_nmap_masscan.txt"
PIDFile_resolve_OG = dirname + sep + "important/PID_resolve_OG.txt"

PY_DivideIP = dirname + sep + "AutoCode/DivideIP.py"
PY_find_useful_file = dirname + sep + "AutoCode/find_useful_file_v4.py"
PY_masscan = dirname + sep + "AutoCode/masscan_v8.py"
PY_masscanFile_resolve = dirname + sep + "AutoCode/masscanFile_resolve_2.py"
PY_nmap_masscan = dirname + sep + "AutoCode/nmap_masscan3.py"
PY_resolve_OG = dirname + sep + "AutoCode/resolve_OG.py"
PY_Insert = dirname + sep + "AutoCode/Insert2.py"

Log_ps_check = dirname + sep + "important/DispathchAll_log.txt"

def runPY(py_file_path, TheArgs) :
    print("Now running " + py_file_path)
    os.system("python3 " + py_file_path + " " + TheArgs + " &")

def runPY2(py_file_path, TheArgs) :
    print("Now running " + py_file_path)
    os.system("python " + py_file_path + " " + TheArgs + " ")


def checkPID(PID_file_path) :
    f_PID = open(PID_file_path, "r")
    PID = int(f_PID.readline())
    f_PID.close()
    print("Now check " + PID_file_path)
    os.system("ps -A | grep " + str(PID) + " > " + Log_ps_check)
    if (os.path.getsize(Log_ps_check)) :
        return True
    return False

if __name__ == "__main__" :
    #in_txt = input("please input your TXT path:\n")
    in_txt = dirname + sep + "IPRange/Shanghai.txt"
    #0.Clean And Rebuild Dir
    os.system("rm -rf " + dirname + sep + "yun/SH2/R1")
    os.system("rm -rf " + dirname + sep + "yun/SH2/R2")
    os.system("rm -rf " + dirname + sep + "yun/SH2/R3")
    os.system("rm -rf " + dirname + sep + "yun/SH2/R4")
    os.system("rm -rf " + dirname + sep + "yun/SH2/R5")
    os.system("rm -rf " + dirname + sep + "yun/SH2/R6")
    os.system("mkdir " + dirname + sep + "yun/SH2/R1")
    os.system("mkdir " + dirname + sep + "yun/SH2/R2")
    os.system("mkdir " + dirname + sep + "yun/SH2/R3")
    os.system("mkdir " + dirname + sep + "yun/SH2/R4")
    os.system("mkdir " + dirname + sep + "yun/SH2/R5")
    os.system("mkdir " + dirname + sep + "yun/SH2/R6")
    #1.DivideIP
    TheArgs = " -i " + in_txt + " -o " + dirname + sep + "yun/SH2/R1 -t 80 "
    runPY(PY_DivideIP, TheArgs)
    time.sleep(30)
    count1 = 1
    while True :
        answer = checkPID(PIDFile_DivideIP)
        print("DivideIP exist : " + str(answer))
        if answer :
            time.sleep(30)
        else :
            break
    print("Divide Finish!")
    #2.nmap_masscan
    TheArgs = " -i " + dirname + sep + "yun/SH2/R1 -o " + dirname + sep + "yun/SH2/R2 -m 0"
    runPY(PY_nmap_masscan, TheArgs)
    time.sleep(60)
    count2 = 1
    while True :
        answer = checkPID(PIDFile_nmap_masscan)
        print("nmap_masscan exist : " + str(answer))
        if answer:
            time.sleep(60)
        else :
            break
    print("nmap_masscan finish!")
    #3.resolve_OG
    TheArgs = " -i " + dirname + sep + "yun/SH2/R2 -o " + dirname + sep + "yun/SH2/R3 -m 1"
    runPY(PY_resolve_OG, TheArgs)
    time.sleep(30)
    count3 = 1
    while True :
        answer = checkPID(PIDFile_resolve_OG)
        print("resolve_OG exist : " + str(answer))
        if answer:
            time.sleep(30)
        else :
            break
    print("resolve_OG finish!")
    #4.masscanFile_resolve
    TheArgs = " -i " + dirname + sep + "yun/SH2/R3 -o " + dirname + sep + "yun/SH2/R4 -m 0"
    runPY(PY_masscanFile_resolve, TheArgs)
    time.sleep(30)
    count4 = 1
    while True :
        answer = checkPID(PIDFile_masscanFile_resolve)
        print("masscanFile_resolve exist : " + str(answer))
        if answer :
            time.sleep(30)
        else :
            break
    print("masscanFile_resolve finish!")
    #5.masscan
    TheArgs = " -i " + dirname + sep + "/yun/SH2/R4 -o " + dirname + sep + "/yun/SH2/R5 -n " + dirname + sep + "NSE -t 30"
    runPY(PY_masscan, TheArgs)
    time.sleep(60)
    count5 = 1
    while True :
        answer = checkPID(PIDFile_masscan)
        print("masscan exist : " + str(answer))
        if answer :
            time.sleep(60)
        else :
            break
    print("masscan finish!")
    #6.find_useful_file
    TheArgs = " -i " + dirname + sep + "/yun/SH2/R5 -o " + dirname + sep + "/yun/SH2/R6"
    runPY(PY_find_useful_file, TheArgs)
    time.sleep(30)
    count6 = 1
    while True :
        answer = checkPID(PIDFile_find_useful_file)
        print("masscan exist : " + str(answer))
        if answer :
            time.sleep(30)
        else :
            break
    print("find_useful_file finish!")
    #7.insert into databse
    db_config = SETTINGS.DATABASE
    TheArgs = " -i " + dirname + sep + "/yun/SH2/R6" + " -h " + db_config["HOST"] + " -u " + db_config["USER"] + " -p " + db_config["PASSWORD"] + " -n " + db_config["NAME"]
       # this is python 2.7
    runPY2(PY_Insert, TheArgs)
    print("Insert Finish!")
