#include "Headers/dynamicAC.h"
#include "Headers/define.h"
#include "Headers/transform.h"
#include "Headers/readfile.h"
#include "Headers/dynamictool.h"
#include "Headers/matchthread.h"


info start = NULL, cur = NULL, infoend = NULL;


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


string getnextmessage() {
    string result;
    if (cur == NULL) {
        if (filenamesit == filenames.end()) {
            return "none";
        }
        curfilename = *filenamesit;
        ofstream out(outputfilename.c_str() + curfilename);
        out.close();
        initmessagelist(inputfilename + *filenamesit);
    }
    result = cur->message;
    curhost = cur->host;
    curport = cur->port;
    curmessage = result;
    cur = cur->next;
    return result;
}

void initmessagelist(string filename) {
    cout << filename << endl;
    freeinfo();
    start = NULL;
    cur = NULL;
    infoend = NULL;
    ifstream in(filename.c_str());
    string buff;
    getline(in, buff);
    string host = "";
    int port = 80;
    while (!in.eof()) {
        getline(in, buff);
        if (buff.substr(0, 5) == "HOST:") {
            host = buff.substr(6, buff.find(" PORT:") - 5);
            port = atoi(buff.substr(buff.find("PORT:") + 6, buff.length() - buff.find("PORT:") - 6).c_str());
            getline(in, buff);
            if (buff.substr(0, 8) == "message:") {
                getline(in, buff);
                string tempmessage = "";
                tempmessage = buff;
                getline(in, buff);
                if (start == NULL) {
                    start = (info)malloc(sizeof(information));
                    start->message = (char*)malloc(tempmessage.length() + 100);
                    start->host = (char*)malloc(host.length() + 1);
                    strcpy(start->host, host.c_str());
                    start->port = port;
                    strcpy(start->message, tempmessage.c_str());
                    start->pre = NULL;
                    start->next = NULL;
                    infoend = start;
                }
                else {
                    info temp = (info)malloc(sizeof(information));
                    temp->message = (char*)malloc(tempmessage.length() + 100);
                    temp->host = (char*)malloc(host.length() + 1);
                    strcpy(temp->host, host.c_str());
                    temp->port = port;
                    strcpy(temp->message, tempmessage.c_str());
                    temp->pre = infoend;
                    temp->next = NULL;
                    infoend->next = temp;
                    infoend = temp;
                }
            }
        }
    }
    cur = start;
    getnextfile();
}

void getnextfile() {
    if (filenamesit != filenames.end()) {
        filenamesit ++;
    }
    else {
        cout << "All the files have been analysed!" << endl;
    }
}

void initfilelist() {
    readFileList((char *)inputfilename.c_str(), &filenames);
    filenamesit = filenames.begin();
}

int readFileList(char *basePath, vector<string> *filename) {
    DIR *dir;
    struct dirent *ptr;
    char base[1000];

    if ((dir = opendir(basePath)) == NULL)
    {
        perror("Open dir error...");
        exit(1);
    }

    while ((ptr=readdir(dir)) != NULL)
    {
        if(strcmp(ptr->d_name,".")==0 || strcmp(ptr->d_name,"..")==0)
            continue;
        else if(ptr->d_type == 8) {
            char temp[100];
            sprintf(temp, "%s/%s", basePath, ptr->d_name);
            string path = temp;
            filename->push_back(ptr->d_name);
        }    ///file
        else if(ptr->d_type == 10)    ///link file
            printf("d_name:%s/%s\n",basePath,ptr->d_name);
        else if(ptr->d_type == 4)    ///dir
        {
            memset(base,'\0',sizeof(base));
            strcpy(base,basePath);
            strcat(base,"/");
            strcat(base,ptr->d_name);
            readFileList(base, filename);
        }
    }
    closedir(dir);
    cout << (*filename).size() << endl;
    return 1;
}

void initweight() {
    ifstream in(weightfilename.c_str());
    weight.clear();
    while (!in.eof()) {
        string buff;
        getline(in, buff);
        string key = buff.substr(0, buff.find(" "));
        double value = atof(buff.substr(buff.find(" ")).c_str());
        weight[key] = value;
    }
}


void freeinfo() {
    if (start != NULL) {
        for (cur = start; cur != NULL; cur = cur->next) {
            info temp = cur->next;
            if (cur->next != NULL) {
                cur->next->pre = NULL;
            }
            cur->next = NULL;
            free(cur->host);
            cur->host = NULL;
            free(cur->message);
            cur->message = NULL;
            free(cur);
            cur = NULL;
            cur = temp;
            if (cur == NULL) {
                break;
            }
        }
    }
}

