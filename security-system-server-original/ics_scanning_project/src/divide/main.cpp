#include "Headers/dynamicAC.h"
#include "Headers/define.h"
#include "Headers/transform.h"
#include "Headers/readfile.h"
#include "Headers/dynamictool.h"
#include "Headers/matchthread.h"

Tree root;
Tree root1;
char pattern[patternnum][patternlength] = {{'\0'}};
int patternnumber = 0;
int pattnum = 0;
long number = 15;
bool finish = false;
int rootnum = 0;
int threadrootnum = 0;
pthread_t id;
pthread_mutex_t mutex;
vector<string> filenames;
string patternfilename;
string inputfilename;
string outputfilename;
string weightfilename;
string curfilename;
vector<string>::iterator filenamesit;
string curhost;
int curport = 0;
string curmessage;
map<string, double> weight;
int scadanum = 0;
int ipcameranum = 0;
int totalnum = 0;

namespace light {
    int mkpath(std::string s,mode_t mode=0755) {
        size_t pre=0,pos;
        std::string dir;
        int mdret;
        if(s[s.size()-1]!='/') {
            // force trailing / so we can handle everything in loop
            s+='/';
        }
        while((pos=s.find_first_of('/',pre))!=std::string::npos) {
            dir=s.substr(0,pos++);
            pre=pos;
            if(dir.size()==0) continue; // if leading / first time is 0 length
            if((mdret=::mkdir(dir.c_str(),mode)) && errno!=EEXIST){
                return mdret;
            }
        }
    return mdret;
    }
}

long getCurrentTime() {
   struct timeval tv;
   gettimeofday(&tv,NULL);
   return tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

void initpattern() {
    getpatterns(pattern, patternfilename);
    pattnum = patternnumber;
    root=buildingTree();
    buildingFailPath(root);
    root1=buildingTree();
    buildingFailPath(root1);
    cout << "initial pattern success, have built the root and root1." << endl;
}

void addpatternsfromfile(Tree temproot, int num, string filename) {
    cout << "add to root" << num << "!" << endl;
    char addpatterns[patternnum][patternlength] = {{'\0'}};
    getpatterns(addpatterns, filename);
    initweight();
    for (int i = 0; addpatterns[i][0] != '\0'; i ++) {
        string ss = addpatterns[i];
        //cout << ss << endl;
        addpattern(temproot, ss, number ++);
    }
    buildingFailPath(temproot);
    rootnum = num;
}

void deletepatternsfromfile(Tree temproot, int num, string filename) {
    cout << "delete from root" << num << "!" << endl;
    char deletepatterns[patternnum][patternlength] = {{'\0'}};
    getpatterns(deletepatterns, filename);
    initweight();
    for (int i = 0; deletepatterns[i][0] != '\0'; i ++) {
        string ss = deletepatterns[i];
        deletepattern(temproot, ss);
    }
    buildingFailPath(temproot);
    rootnum = num;
}

int main(int argc, char* argv[])
{
    for (int i = 1; i <= argc-1; i ++) {
        string s = argv[i];
        if (s == "-i") {
            inputfilename = argv[++ i];
        }
        else if (s == "-o") {
            outputfilename = argv[++ i];
            light::mkpath(outputfilename);
        }
        else if (s == "-p") {
            patternfilename = argv[++ i];
        }
        else if (s == "-w") {
            weightfilename = argv[++ i];
        }
        else {
            cout << "Please use arguments -i with your input files' absolute path and -o with the output files' absolute path and -p with the patters file's path and -w with the weight file's path." << endl;
            return 0;
        }
    }
    initfilelist();
    initweight();


    initpattern();
    pthread_mutex_init (&mutex,NULL);
    int res = pthread_create(&id, NULL, matchthread, NULL);
    //matchthread();
    if (res) {
        cout << "create thread failed!" << endl;
    }

    while (true) {
        char order1[10] = {'\0'};
        char order2[100] = {'\0'};
        cout << "HERE!" << endl;
        scanf("%s %s", order1, order2);
        cout << "HERE2!" << endl;
        string s1 = order1;
        string s2 = order2;
        if (s1 == "-a") {
            if (rootnum == 0) {
                addpatternsfromfile(root1, 1, s2);
                while (true) {
                    cout << threadrootnum << "HERE1!" << endl;
                    cout << "please wait to the other root to update!" << endl;
                    sleep(1);
                    pthread_mutex_lock(&mutex);
                    if (threadrootnum == 1) {
                        break;
                    }
                    pthread_mutex_unlock(&mutex);
                }
                pthread_mutex_unlock(&mutex);
                addpatternsfromfile(root, 1, s2);
            }
            else {
                addpatternsfromfile(root, 0, s2);
                while (true) {
                    cout << threadrootnum << "HERE2!" << endl;
                    cout << "please wait to the other root to update!" << endl;
                    sleep(1);
                    pthread_mutex_lock(&mutex);
                    if (threadrootnum == 0) {
                        break;
                    }
                    pthread_mutex_unlock(&mutex);
                }
                pthread_mutex_unlock(&mutex);
                cout << "HERE3!" << endl;
                addpatternsfromfile(root1, 0, s2);
            }
        }
        else if (s1 == "-d") {
            if (rootnum == 0) {
                deletepatternsfromfile(root1, 1, s2);
                while (threadrootnum != 1) {
                    cout << "please wait to the other root to update!" << endl;
                    sleep(1);
                }
                deletepatternsfromfile(root, 1, s2);
            }
            else {
                deletepatternsfromfile(root, 0, s2);
                while (threadrootnum != 0) {
                    cout << "please wait to the other root to update!" << endl;
                    sleep(1);
                }
                deletepatternsfromfile(root1, 0, s2);
            }
        }
        else {
            cout << "please input correct order such as -a filename to add patterns or -d filename to delete patterns." << endl;
        }
        if (finish) {
            break;
        }
    }

    return 0;
}
