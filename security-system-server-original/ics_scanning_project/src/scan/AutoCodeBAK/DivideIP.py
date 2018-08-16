import getopt
import sys
import os

def writePID() :
    dirdirname = os.path.dirname(os.path.dirname(__file__))
    f_PID = open(dirdirname + "/important/PID_DivideIP.txt", "w")
    f_PID.write(str(os.getpid()))
    f_PID.close()
    
def IP2Number(ip) :
    ip1, ip2, ip3, ip4 = ip.split(".")
    return (((int(ip1) * 256 + int(ip2)) * 256 + int(ip3)) * 256) + int(ip4)
def Number2IP(number) :
    ip4 = int(number) % 256
    ip3 = int((number - ip4) / 256) % 256
    ip2 = int((number - ip4 - ip3) / 256 / 256) % 256
    ip1 = int((number - ip4 - ip3 - ip2) / 256 /256 /256) % 256
    return str(ip1) + "." + str(ip2) + "." + str(ip3) + "." + str(ip4)
def usageDVIP() :
    print("-i : in-file path\n-o : out-file path\n-t : ThreadNumber")

#in_file = input("input your in-file path\n")
#out_file = input("input your out-file dir\n")
#ThreadNumber = int(input("input your thread number\n"))
opts, args = getopt.getopt(sys.argv[1: ], "i:o:t:u:")
for op, value in opts :
    if op == "-i" :
        in_file = value
    elif op == "-o" :
        out_file = value
    elif op == "-t" :
        ThreadNumber = int(value)
    else :
        usageDVIP()
        sys.exit()
writePID()
f_in = open(in_file, "r")
lines = f_in.readlines()
f_in.close()
BEFORE= []
TOTAL = 0
for eachline in lines :
    eachline = eachline.rstrip().lstrip()
    tmpeachline = eachline.split("\t")
    begin = tmpeachline[0]
    end = tmpeachline[1]
    mid = IP2Number(end) - IP2Number(begin) + 1
    TOTAL += mid
    BEFORE.append([begin, end, mid])
print(BEFORE)
print("Total Number : " + str(TOTAL))
EACH = TOTAL / ThreadNumber
# divide
AFTER = {}
for i in range(0, ThreadNumber):
    now_number = 0
    AFTER[i] = []
    for item in BEFORE :
        if (item[2] + now_number) < EACH :
            now_number += item[2]
            AFTER[i].append([item[0], item[1], item[2]])
        else :
            AFTER[i].append([item[0], Number2IP(IP2Number(item[0]) + EACH - now_number) ])
            item[0] = Number2IP(IP2Number(item[0]) + EACH - now_number + 1)
            item[2] = IP2Number(item[1]) - IP2Number(item[0])
            break
    for item in AFTER[i] :
        if item in BEFORE:
            BEFORE.remove(item)
            item.remove(item[2])
print(AFTER)
CHECK = 0
for items in AFTER :
    for item in AFTER[items] :
        CHECK += IP2Number(item[1]) - IP2Number(item[0]) + 1
if CHECK != TOTAL :
    print("Wrong divide!")

for items in AFTER :
    f_out = open(out_file + "/" + str(items) + ".txt", "w")
    for item in AFTER[items] :
        begin = IP2Number(item[0])
        end = IP2Number(item[1])
        for i in range(begin, end + 1) :
            f_out.write(Number2IP(i) + "\n")
    f_out.close()
