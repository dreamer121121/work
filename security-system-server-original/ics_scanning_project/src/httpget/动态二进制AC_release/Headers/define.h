#ifndef DEFINE_H_INCLUDED
#define DEFINE_H_INCLUDED



#endif // DEFINE_H_INCLUDED

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <string>
#include <string.h>
#include <sys/time.h>
#include <signal.h>
#include <malloc.h>
#include <queue>
#include <fstream>
#include <cstdio>
#include <sstream>
#include <vector>
#include <pthread.h>
#include <map>
using namespace std;


#define BUFFER_SIZE 1024
#define HTTP_POST "POST /%s HTTP/1.1\r\nHOST: %s:%d\r\nAccept: */*\r\n"\
    "Content-Type:application/octet-stream/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s"
#define HTTP_GET "GET /%s HTTP/1.1\r\nHOST: %s:%d\r\nAccept: */*\r\n\r\nContent-Type:application/octet-stream\r\n\r\n"
#define BUFFER_LENGTH 100
#define BUFFER_MAX 65535
#define ASIZE 256
#define MAX(a, b)  (((a) > (b)) ? (a) : (b))
#define ITEMMAX 1000
#define patternnum 10000

#define patternlength 50

struct target {
    char *host;
    int port;
};


struct ARGS {
   string filename;
   int threadid;
};




extern char pattern[patternnum][patternlength];
extern int patternnumber;
extern int pattnum;
extern Tree root;
extern Tree root1;
extern long number;
extern bool finish;
extern int rootnum;
extern int threadrootnum;
extern pthread_t id;
extern pthread_mutex_t mutex;





