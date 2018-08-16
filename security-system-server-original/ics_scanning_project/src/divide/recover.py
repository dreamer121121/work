# -*- coding: utf-8 -*-
import binascii
import codecs
import os
import sys
import getopt
import json, yaml


pathDir = ""
infilepath = ""
outfilepath = ""

def usage():
    print "please use -i to set inputfilepath and -o to set outputfilepath\r\n"

def handler(fin, fout) :
    line = fin.readline()
    while line :
        message = ""
        if line.rstrip() == "--------------------------------------------------" :
            fout.write(line.rstrip() + "\n")
            line = fin.readline()
            fout.write(line.rstrip() + "\n")
            line = fin.readline()
            fout.write(line.rstrip() + "\n")
            line = fin.readline()
            while line.rstrip() != "--------------------------------------------------" :
                if line :
                    print line.rstrip()
                    taglist = line.rstrip().split(' ')
                    tags = ""
                    for tag in taglist:
                        fout.write(json.dumps(binascii.a2b_hex(tag)).decode("unicode-escape"))
                        fout.write(" ")
                        # tags += binascii.a2b_hex(tag).decode("utf8", "ignore")+ " "
                    # message += tags
                    fout.write("\n")
                    line = fin.readline()
                    fout.write(line.rstrip() + "\n")
                    line = fin.readline()
                    fout.write(json.dumps(binascii.a2b_hex(line.rstrip())).decode("unicode-escape") + "\n")
                    line = fin.readline()
                else :
                    break
            # fout.write(message + "\n")






opts, args = getopt.getopt(sys.argv[1:], "i:o:")
for op, value in opts :
    if op == "-i" :
        infilepath = value
    elif op == "-o" :
        outfilepath = value
    else :
        usage()
        sys.exit()
pathDir =  os.listdir(infilepath)
for filename in pathDir:
    print filename
    fin = open(infilepath+filename, 'r')
    fout = codecs.open(outfilepath+filename, 'w', 'gb2312')
    handler(fin,fout)
    fin.close()
    fout.close()