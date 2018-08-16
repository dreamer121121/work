#include "Headers/dynamicAC.h"
#include "Headers/define.h"
#include "Headers/transform.h"
#include "Headers/readfile.h"
#include "Headers/dynamictool.h"
#include "Headers/matchthread.h"





void getpatterns(char pattern[patternnum][patternlength], string name) {
    ifstream in(name.c_str());
    int i = 0;
    while (!in.eof()) {
        string buff;
        getline(in, buff);
        strcpy(pattern[i], buff.c_str());
        i ++;
    }
    patternnumber = i;
    in.close();
}


string getmessage(string filename) {
    ifstream in(filename.c_str());
    string result;
    while (!in.eof()) {
        string buff;
        getline(in, buff);
        //buff += "00";
        result += buff;
    }
    return result;
}

