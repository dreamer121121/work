import os
import time

pid_file_name = "/root/PLC/important/PID_getPID.txt" 

def main():
    #print(os.getpid())
    #print(os.getppid())
    f = open(pid_file_name, "w")
    f.write(str(os.getpid()))
    f.close()

if __name__ == "__main__":
    main()
    t = 1
    while t < 10:
        time.sleep(2)
        t += 1
