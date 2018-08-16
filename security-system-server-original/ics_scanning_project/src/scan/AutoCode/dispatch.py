import os
import time

getPID_PID = -1
getPID_PIDfile = "/root/PLC/important/PID_getPID.txt" 

def run_getPID() :
    os.system("python3 /root/py/getPID.py &")
    print(1)
    

def check_getPID() :
    """
    if os.path.exists("/root/PLC/important/dispatch_log.txt") :
        os.system("rm /root/PLC/important/dispatch_log.txt")\
    """
    f = open(getPID_PIDfile, "r")
    PID = int(f.readline())
    print(str(PID))
    f.close()
    os.system("ps -A | grep " + str(PID) + " > /root/PLC/important/dispatch_log.txt")
    if (os.path.getsize("/root/PLC/important/dispatch_log.txt")) :
        return True #exist
    return False

if __name__ == "__main__" :
    run_getPID()
    time.sleep(3)
    t = 1
    while t < 20 :
        answer = check_getPID()
        print("the file is : " + str(answer))
        if answer : #exist
            time.sleep(3)
        else :
            break
    print("over!")
