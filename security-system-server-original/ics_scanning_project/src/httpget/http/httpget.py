# coding:utf-8
import os
import sys
import pycurl
import StringIO, cStringIO
import getopt
import threading
import thread
import time
import codecs



# arg[0] = host
# arg[1] = port
# arg[2] = filename
# arg[3] = inputfilepath
# arg[4] = outputfilepath
# arg[5] = list of hosts
# arg[6] = pos of hostlist
# arg[7] = list of files
# arg[8] = pos of filelist
# arg[9] = no
# arg[10] = lock



class httpthread(threading.Thread):
    """docstring for httpthread"""
    def __init__(self, arg):
        super(httpthread, self).__init__()
        self.arg = arg
    def run(self):
        global lock
        global filename
        global hostlist
        global hostlistpos
        global filelist
        global filelistpos
        global inputfilepath
        global outputfilepath
        # global log
        global finish
        while True:
            if finish:
                break
            host = hostlist[hostlistpos][0]
            port = hostlist[hostlistpos][1]
            lock.acquire()
            self.getnexthost()
            print host + " " + port + " start ..."
            # log.write(host + " " + port + " start ...\n")
            # log.write(str(time.time()) + " threadid = " + str(self.arg) + "\n")
            lock.release()
            self.handler(host, port, outputfilepath, filename)

    def handler(self, host, port, outputfilepath, filename):
        # global log
        url = host + ":" + port
        c = pycurl.Curl()
        b = StringIO.StringIO()
        c.setopt(pycurl.CONNECTTIMEOUT, 1)
        c.setopt(pycurl.TIMEOUT, 2)
        c.setopt(pycurl.NOPROGRESS, 0)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.FORBID_REUSE, 1)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.USERAGENT,"Mozilla/5.2 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50324)")
        c.setopt(pycurl.HTTPHEADER, ["Accept:"])
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.CUSTOMREQUEST, "GET")
        c.setopt(pycurl.HEADER, 1)
        c.setopt(c.WRITEFUNCTION, b.write)
        c.setopt(pycurl.NOSIGNAL, 1)
        global filelock
        try :
            c.perform()
            s = b.getvalue()
            filelock.acquire()
            fout = open(outputfilepath + filename, 'a')
            fout.write("--------------------------------------------------\n")
            fout.write("HOST: " + host + " PORT: " + port + "\n")
            fout.write("message:\n")
            fout.write(s)
            fout.write("\n")
            fout.close()
            filelock.release()
        except Exception, e :
            print e
            #print "\n[*] HOST: " + host + " PORT: " + port + " connect timeout ..."
            # log.write("[*] HOST: " + host + " PORT: " + port + " connect timeout ...\n")
        b.close()
        c.close()

    def getnexthost(self):
        global filename
        global hostlist
        global hostlistpos
        global filelist
        global filelistpos
        global inputfilepath
        global outputfilepath
        # global log
        global finish
        if hostlistpos == len(hostlist) - 1:
            if filelistpos == len(filelist) - 1:
                print "All the files have handlered successfully."
                # log.write("All the files have handlered successfully.\n")
                # log.close()
                finish = True
            else:
                filelistpos = filelistpos + 1
                filename = filelist[filelistpos]
                # log.write("----------" + filename + "\n")
                fout = codecs.open(outputfilepath + filename, 'w', 'utf-8')
                fout.close()
                hostlist = []
                fin = open(inputfilepath + filename)
                line = fin.readline()
                while line:
                    linelist = line.rstrip().split("\t\t")
                    host = linelist[0]
                    port = linelist[1]
                    hostlist.append([host, port])
                    line = fin.readline()
                fin.close()
                hostlistpos = 0
                if len(hostlist) == 0:
                    self.getnexthost()
        else:
            hostlistpos = hostlistpos + 1



def usage():
    print "please use -f to set filepath"


def handleronefile(inputfilepath, filename, outputfilepath) :
    fin = open(inputfilepath + filename)
    fout = open(outputfilepath + filename, 'w')
    line = fin.readline()
    while line :
        linelist = line.rstrip().split("\t\t")
        ip = linelist[0]
        port = linelist[1]
        url = ip + ":" + port
        c = pycurl.Curl()
        b = StringIO.StringIO()
        c.setopt(pycurl.CONNECTTIMEOUT, 0)
        c.setopt(pycurl.TIMEOUT, 2)
        c.setopt(pycurl.NOPROGRESS, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.FORBID_REUSE, 1)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.USERAGENT,"Mozilla/5.2 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50324)")
        c.setopt(pycurl.HTTPHEADER, ["Accept:"])
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.CUSTOMREQUEST, "GET")
        c.setopt(pycurl.HEADER, 1)
        c.setopt(c.WRITEFUNCTION, b.write)
        try :
            c.perform()
            s = b.getvalue()
            fout = open(outputfilepath + filename, 'a')
            fout.write("--------------------------------------------------\n")
            fout.write("HOST: " + ip + " PORT: " + port + "\n")
            fout.write("message:\n")
            fout.write(s)
            fout.write("\n")
            fout.close()
        except Exception, e :
            print "\n[*] HOST: " + ip + " PORT: " + port + " connect timeout ..."
        b.close()
        c.close()
        line = fin.readline()
    fin.close()

#def getPort(filename)
#    for i in range(len(filename)):
#        if i != '_':
#            port +=filename[i]


def eachFile(inputfilepath, outputfilepath, filelist):
    pathDir =  os.listdir(inputfilepath)
    for allDir in pathDir:
        filelist.append(allDir)


opts, args = getopt.getopt(sys.argv[1:], "i:o:t:")
for op, value in opts :
    if op == "-i" :
        inputfilepath = value
    elif op == "-o" :
        outputfilepath = value
    elif op == "-t" :
        threadnum = value
    else :
        usage()
        sys.exit()

# eachFile(inputfilepath, outputfilepath)
filelist = []
hostlist = []
eachFile(inputfilepath, outputfilepath, filelist)
if len(filelist) != 0:
    filename = filelist[0]
    fin = open(inputfilepath + filename)
    fout = codecs.open(outputfilepath + filename, 'w', 'utf-8')
    fout.close()
    line = fin.readline()
    while line:
        linelist = line.rstrip().split("\t\t")
        host = linelist[0]
        port = linelist[1]
        hostlist.append([host, port])
        line = fin.readline()
    if len(hostlist) == 0:
        print "please modify the files input to avoid exist null file."
        sys.exit()
print filelist
lock = threading.Lock()
filelock = threading.Lock()
#filename = filelist[0]
hostlistpos = 0
filelistpos = 0
finish = False
# log = open(outputfilepath + "log.txt", 'w')
for i in xrange(int(threadnum)):
    # arg = []
    # arg.append(hostlist[0][0])
    # arg.append(hostlist[0][1])
    # arg.append(filelist[0])
    # arg.append(inputfilepath)
    # arg.append(outputfilepath)
    # arg.append(hostlist)
    # arg.append(0)
    # arg.append(filelist)
    # arg.append(0)
    # arg.append(i)
    # arg.append(lock)
    t = httpthread(i)
    t.start()

while True:
    if finish:
        break
    time.sleep(1)









