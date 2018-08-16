#ifndef DEFINE_H_INCLUDED
#define DEFINE_H_INCLUDED



#endif // DEFINE_H_INCLUDED


#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <vector>
#include <fstream>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/shm.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/time.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <malloc.h>
#include <sstream>
#include "fileop.h"
#include "client.h"
#include "mythread.h"
#include <time.h>
#include <sys/stat.h>
#include <errno.h>


#define threadmaxruntime 2


using namespace std;

struct target {
    char *host;
    int port;
};

extern vector<int> threadid;
extern vector<bool> threadfree;
extern vector<struct target> threadtarget;
extern vector<string> threadoutfile;
extern ofstream logout;
extern int successnum;



