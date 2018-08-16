import os
import sys
import getopt

def usage():
    print "please use -f to set filepath"


def eachFile(filepath):
    pathDir =  os.listdir(filepath)
    i = 0
    j = 0
    for allDir in pathDir:
        i = i + 1
        f = open(filepath + allDir, 'r')
        length = len(f.readlines())
        print filepath + allDir
        if length == 0:
            j = j + 1
            f.close()
            os.system("rm -rf " + filepath + allDir)
        f.close()
    print i
    print j


opts, args = getopt.getopt(sys.argv[1:], "f:")
for op, value in opts :
    if op == "-f" :
        filepath = value
    else :
        usage()
        sys.exit()


sys.setrecursionlimit(1000000)
# filepath = "R2_primitive_new2/R3_R2_primitive_new_1_result/"
eachFile(filepath)
