#ifndef READFILE_H_INCLUDED
#define READFILE_H_INCLUDED



#endif // READFILE_H_INCLUDED

#include <string>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>

using namespace std;

typedef struct information {
    char *host;
    int port;
    char *message;
    struct information* pre;
    struct information* next;
} Information, *info;

extern info start, cur, infoend;


void getpatterns(char pattern[patternnum][patternlength], string name);
string getmessage(string filename);
string getnextmessage();
void initmessagelist(string filename);
void getnextfile();
void initfilelist();
int readFileList(char *basePath, vector<string> *filename);
void initweight();
void freeinfo();

