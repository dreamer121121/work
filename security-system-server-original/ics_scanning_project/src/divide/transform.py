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
	all_text = fin.read()
	transform = binascii.b2a_hex(all_text.decode("gb2312","ignore").encode("utf-8"))
	fout.write(transform)
	fin.close()
	fout.close()
