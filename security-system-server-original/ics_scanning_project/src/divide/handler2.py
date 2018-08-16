import binascii
import codecs
import os
import sys
import getopt


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
                    #print line.rstrip()
                    message += binascii.b2a_hex(line.rstrip().lower().replace(' ', '').replace('\t', '').decode("gb2312","ignore").encode("utf-8"))
                    line = fin.readline()
                else :
                    break
            fout.write(message + "\n")






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
    fout = codecs.open(outfilepath+filename, 'w', 'utf-8')
    handler(fin,fout)
    fin.close()
    fout.close()