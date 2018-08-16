#include "Headers/define.h"

string filepath;
string targetfilepath;
int threadnum = 0;
int successnum = 0;
vector<string> files;
vector<int> threadid;
vector<bool> threadfree;
vector<struct target> threadtarget;
vector<string> threadoutfile;
vector<long> threadtime;
vector<int> threadtimes;
pthread_mutex_t mutex;
ofstream logout;


long getcurrenttime() {
    struct timeval tv;
    gettimeofday(&tv,NULL);
    return (tv.tv_sec*1000 + tv.tv_usec/1000);
}

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



int main(int argc, char* argv[])
{
    long t0 = getcurrenttime();
    for (int i = 1; i <= argc-1; i ++) {
        string s = argv[i];
        if (s == "-n") {
            filepath = argv[++ i];
        }
        else if (s == "-t") {
            threadnum = atoi(argv[++ i]);
        }
        else if (s == "-f") {
            targetfilepath = argv[++ i];
            light::mkpath(targetfilepath);
        }
        else {
            cout << "Please use arguments -n with your file's absolute path and -t with the number of threads and -f with the target file path to init." << endl;
            return 0;
        }
    }
    //open((filepath + "/result/" + "log.txt").c_str(), (O_CREAT|O_WRONLY|O_TRUNC));
    logout.open((targetfilepath + "log.txt").c_str(), ios::in|ios::out);
    if (!logout.is_open()) {
        string logoutfilepath = targetfilepath + "log.txt";
        open(logoutfilepath.c_str(), (O_CREAT|O_WRONLY|O_TRUNC));
        logout.open(logoutfilepath.c_str());
    }
    for (int i = 1; i <= threadnum; i ++) {
        threadid.push_back(i);
        threadfree.push_back(true);
        struct target temptar;
        threadtarget.push_back(temptar);
        threadoutfile.push_back(targetfilepath);
        threadtime.push_back(time((time_t*)NULL));
        threadtimes.push_back(0);
    }
    pthread_t id[threadnum];
    readFileList((char*)filepath.c_str(), &files);
    vector<string>::iterator it;
    int busy = 0;
    for (it = files.begin(); it != files.end(); it ++) {
        ifstream in(filepath + *it);
        ofstream out(targetfilepath + *it);
        if (!out.is_open()) {
            string outfilepath = targetfilepath + *it;
            open(outfilepath.c_str(), (O_CREAT|O_WRONLY|O_TRUNC));
            ofstream(targetfilepath + *it);
        }
        out.close();
        while (!in.eof()) {
            int i = 0;
            char line[256] = {'\0'};
            char host[20] = {'\0'};
            struct target tar;
            tar.port = 0;
            in.getline(line, 100);
            if (line[0] == '\0') {
                break;
            }
            for (i = 0; line[i] != '\t'; i ++) {
                host[i] = line[i];
            }
            tar.host = host;
            for (i += 2; line[i] != '\0' && line[i] != '\r' && line[i] != '\n'; i ++) {
                tar.port = tar.port*10 + (line[i] - '0');
            }
            logout << tar.host << " start!!!" << endl;
            cout << tar.host << " start!!!" << endl;
            while (true) {
                int flag = 0;
                vector<int>::iterator threadidit;
                for (threadidit = threadid.begin(); threadidit != threadid.end(); threadidit ++) {
                    if (threadfree.at(*threadidit-1)) {
                        threadtarget.at(*threadidit-1) = tar;
                        threadfree.at(*threadidit-1) = false;
                        threadoutfile.at(*threadidit-1) = targetfilepath + *it;
                        int *paraid = (int*)malloc(sizeof(int));
                        *paraid = *threadidit;
                        threadtime.at(*threadidit-1) = time((time_t*)NULL);
                        threadtimes.at(*threadidit-1) = 0;
                        int res = pthread_create(&id[*threadidit-1], NULL, mythread, (void*)paraid);
                        if (res) {
                            string s = "create the thread " + to_string(*threadidit) + " failed!";
                            cout << s << endl;
                            logout << s << endl;
                        }
                        else {
                            flag = 1;
                            break;
                        }
                    }
                    else {
                        threadtimes.at(*threadidit-1) ++;
                        if (threadtimes.at(*threadidit-1) >= 1000*threadnum) {
                            cout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                            logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                            pthread_cancel(id[*threadidit-1]);
                            pthread_detach(id[*threadidit-1]);
                            threadfree.at(*threadidit-1) = true;
                            threadtimes.at(*threadidit-1) = 0;
                        }
                        //if (time((time_t*)NULL) - threadtime.at(*threadidit-1) > threadnum) {
                            //cout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                            //logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                            //pthread_cancel(id[*threadidit-1]);
                            //threadfree.at(*threadidit-1) = true;
                            //threadtimes.at(*threadidit-1) = 0;
                        //}
                    }
                }
                if (flag == 1) {
                    busy = 0;
                    break;
                }
                else {
                    busy ++;
                }
                if (busy >= 1000*threadmaxruntime) {
                    busy = 0;
                    for (threadidit = threadid.begin(); threadidit != threadid.end(); threadidit ++) {
                        cout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                        logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                        pthread_cancel(id[*threadidit-1]);
                        pthread_detach(id[*threadidit-1]);
                        threadfree.at(*threadidit-1) = true;
                        threadtimes.at(*threadidit-1) = 0;
                    }
                }
                usleep(1000);
            }
        }
        in.close();

    }
    long t1 = getcurrenttime();
    sleep(10);
    cout << "All the threads have finished!!!" << endl;
    logout << "RUNTIME: " << t1-t0 << " ms" << endl;
    logout << "RUNTIME: " << (t1-t0)/1000 << " s" << endl;
    logout << "RUNTIME: " << (t1-t0)/1000/3600 << " h" << endl;
    logout << "successnum: " << successnum << endl;
    logout << "All the threads have finished!!!" << endl;
    logout.close();
    return 0;
}