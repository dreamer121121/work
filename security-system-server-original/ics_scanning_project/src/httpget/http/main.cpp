#include "Headers/define.h"
#include <exception>

string filepath;
string targetfilepath;
int threadnum = 0;
int successnum = 0;
vector<string> files;
vector<int> threadid;
vector<bool> threadfree;
vector<struct target*> threadtarget;
vector<string> threadoutfile;
vector<long> threadtime;
vector<int> threadtimes;
pthread_mutex_t mutex;
pthread_mutex_t mutex2;
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
    // open((filepath + "/result/" + "log.txt").c_str(), (O_CREAT|O_WRONLY|O_TRUNC));
    logout.open((targetfilepath + "log.txt").c_str(), ios::in|ios::out);
    if (!logout.is_open()) {
        string logoutfilepath = targetfilepath + "log.txt";
        open(logoutfilepath.c_str(), (O_CREAT|O_WRONLY|O_TRUNC));
        logout.open(logoutfilepath.c_str());
    }
    for (int i = 1; i <= threadnum; i ++) {
        threadid.push_back(i);
        threadfree.push_back(true);
        struct target* temptar = (struct target*)malloc(sizeof(struct target));
        temptar->host = (char*)malloc(sizeof(100));
        threadtarget.push_back(temptar);
        threadoutfile.push_back("");
        threadtime.push_back(time((time_t*)NULL));
        threadtimes.push_back(0);
    }
    pthread_t id[threadnum];
    readFileList((char*)filepath.c_str(), &files);
    vector<string>::iterator it;
    int busy = 0;
    for (it = files.begin(); it != files.end(); it ++) {
        // ifstream in(filepath + *it);
        // ifstream out(targetfilepath + *it);
        string outfilepath = targetfilepath + *it;
        // if (!out.is_open()) {
        //     open(outfilepath.c_str(), (O_CREAT|O_WRONLY|O_TRUNC));
        // }
        // out.close();
        // out.clear();
        // ofstream tempout(outfilepath.c_str());
        // logout << "out" << tempout.is_open() << endl;
        // tempout << "test!" << endl;
        // tempout.close();
        // tempout.clear();
        // ifstream tempin(outfilepath.c_str());
        // string templine;
        // getline(tempin, templine);
        // logout << templine << endl;
        // tempin.close();
        // tempin.clear();
        // tempin.open(filepath + *it);
        // logout << "in" << tempin.is_open() << endl;
        // getline(tempin, templine);
        // tempin.close();
        // tempin.clear();
        FILE* f;
        f = fopen((char*)(outfilepath.c_str()), "w");
        if (f == NULL) {
            cout << filepath + *it << " open file failed!" << endl;
            logout << filepath + *it << " open file failed!" << errno << endl;
            continue;
        }
        fclose(f);
        cout << (filepath + *it).c_str() << endl;
        f = fopen((char*)((filepath + *it).c_str()), "r");
        if (f == NULL) {
            cout << filepath + *it << " open file failed!" << endl;
            logout << filepath + *it << " open file failed!" << errno << endl;
            continue;
        }
        // logout << templine << endl;
        // logout << outfilepath.c_str() << endl;
        char host[50] = {'\0'};
        int port = 0;
        while (fscanf(f, "%s\t\t%d", host, &port)) {
            try {
            if (host[0] == '\0') {
                break;
            }
            //cout << host << endl;
            int i = 0;
            string fileline;
            char line[256] = {'\0'};
            struct target* tar = (struct target*)malloc(sizeof(struct target));
            if (tar == NULL) {
                cout << "can't alloc memory!" << endl;
                continue;
            }
            tar->port = port;
            tar->host = (char*)malloc(sizeof(100));
            if (tar->host == NULL) {
                cout << "can't alloc memory!" << endl;
                continue;
            }
            strcpy(tar->host, host);
            // logout << tar.host << " start!!!" << endl;
            // cout << tar->host << " start!!!" << endl;
            while (true) {
                int flag = 0;
                vector<int>::iterator threadidit;
                for (threadidit = threadid.begin(); threadidit != threadid.end(); threadidit ++) {
                    if (threadfree.at(*threadidit-1)) {
                        //free(threadtarget.at(*threadidit-1));
                        strcpy(threadtarget.at(*threadidit-1)->host, tar->host);
                        threadtarget.at(*threadidit-1)->port = tar->port;
                        free(tar);
                        threadfree.at(*threadidit-1) = false;
                        threadoutfile.at(*threadidit-1) = targetfilepath + *it;
                        int *paraid = (int*)malloc(sizeof(int));
                        if (paraid == NULL) {
                            cout << "can't alloc memory!" << endl;
                            continue;
                        }
                        *paraid = *threadidit;
                        threadtime.at(*threadidit-1) = time((time_t*)NULL);
                        threadtimes.at(*threadidit-1) = 0;
                        int res = pthread_create(&id[*threadidit-1], NULL, mythread, (void*)paraid);
                        if (res) {
                            string s = "create the thread " + to_string(*threadidit) + " failed!";
                            cout << s << endl;
                            // logout << s << endl;
                        }
                        else {
                            flag = 1;
                            break;
                        }
                    }
                    else {
                        threadtimes.at(*threadidit-1) ++;
                        if (threadtimes.at(*threadidit-1) >= 1000*threadnum) {
                            // cout << threadtarget.at(*threadidit-1)->host << " overtime!" << endl;
                            // logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                            pthread_mutex_lock(&mutex2);
                            if (threadfree.at(*threadidit-1) == false) {
                            // int kill_rc = pthread_kill(id[*threadidit-1], 0);
                            // if(kill_rc != ESRCH) {
                                pthread_cancel(id[*threadidit-1]);
                                pthread_detach(id[*threadidit-1]);
                            // }
                            }
                            pthread_mutex_unlock(&mutex2);
                            threadfree.at(*threadidit-1) = true;
                            threadtimes.at(*threadidit-1) = 0;
                            pthread_mutex_unlock(&mutex);
                            //free(threadtarget.at(*threadidit-1));
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
                        // cout << threadtarget.at(*threadidit-1)->host << " overtime!" << endl;
                        // logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
                        pthread_mutex_lock(&mutex2);
                        if (threadfree.at(*threadidit-1) == false) {
                            // int kill_rc = pthread_kill(id[*threadidit-1], 0);
                            // if(kill_rc != ESRCH) {
                            pthread_cancel(id[*threadidit-1]);
                            pthread_detach(id[*threadidit-1]);
                            // }
                        }
                        pthread_mutex_unlock(&mutex2);
                        threadfree.at(*threadidit-1) = true;
                        threadtimes.at(*threadidit-1) = 0;
                        // pthread_mutex_unlock(&mutex);
                        //free(threadtarget.at(*threadidit-1));
                    }
                }
                usleep(1000);
            }
            // cout << host << " distributed!!!" << endl;
            memset(host, '\0', 50);
            } catch(exception e) {
                logout << "WRONG! " << (filepath + *it) << " " << host << " " << port << endl;
                usleep(1000);
                memset(host, '\0', 50);
            }
        }
        // while (!in.eof()) {
        //     int i = 0;
        //     string fileline;
        //     char line[256] = {'\0'};
        //     char host[50] = {'\0'};
        //     struct target* tar = (struct target*)malloc(sizeof(struct target));
        //     tar->port = 0;
        //     getline(in, fileline);
        //     strcpy(line, fileline.c_str());
        //     if (line[0] == '\0') {
        //         break;
        //     }
        //     for (i = 0; line[i] != '\t'; i ++) {
        //         host[i] = line[i];
        //     }
        //     tar->host = (char*)malloc(sizeof(100));
        //     strcpy(tar->host, host);
        //     for (i += 2; line[i] != '\0' && line[i] != '\r' && line[i] != '\n'; i ++) {
        //         tar->port = tar->port*10 + (line[i] - '0');
        //     }
        //     // logout << tar.host << " start!!!" << endl;
        //     cout << tar->host << " start!!!" << endl;
        //     while (true) {
        //         int flag = 0;
        //         vector<int>::iterator threadidit;
        //         for (threadidit = threadid.begin(); threadidit != threadid.end(); threadidit ++) {
        //             if (threadfree.at(*threadidit-1)) {
        //                 //free(threadtarget.at(*threadidit-1));
        //                 strcpy(threadtarget.at(*threadidit-1)->host, tar->host);
        //                 threadtarget.at(*threadidit-1)->port = tar->port;
        //                 free(tar);
        //                 threadfree.at(*threadidit-1) = false;
        //                 threadoutfile.at(*threadidit-1) = targetfilepath + *it;
        //                 int *paraid = (int*)malloc(sizeof(int));
        //                 *paraid = *threadidit;
        //                 threadtime.at(*threadidit-1) = time((time_t*)NULL);
        //                 threadtimes.at(*threadidit-1) = 0;
        //                 int res = pthread_create(&id[*threadidit-1], NULL, mythread, (void*)paraid);
        //                 if (res) {
        //                     string s = "create the thread " + to_string(*threadidit) + " failed!";
        //                     cout << s << endl;
        //                     // logout << s << endl;
        //                 }
        //                 else {
        //                     flag = 1;
        //                     break;
        //                 }
        //             }
        //             else {
        //                 threadtimes.at(*threadidit-1) ++;
        //                 if (threadtimes.at(*threadidit-1) >= 1000*threadnum) {
        //                     cout << threadtarget.at(*threadidit-1)->host << " overtime!" << endl;
        //                     // logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
        //                     pthread_cancel(id[*threadidit-1]);
        //                     pthread_detach(id[*threadidit-1]);
        //                     threadfree.at(*threadidit-1) = true;
        //                     threadtimes.at(*threadidit-1) = 0;
        //                     pthread_mutex_unlock(&mutex);
        //                     //free(threadtarget.at(*threadidit-1));
        //                 }
        //                 //if (time((time_t*)NULL) - threadtime.at(*threadidit-1) > threadnum) {
        //                     //cout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
        //                     //logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
        //                     //pthread_cancel(id[*threadidit-1]);
        //                     //threadfree.at(*threadidit-1) = true;
        //                     //threadtimes.at(*threadidit-1) = 0;
        //                 //}
        //             }
        //         }
        //         if (flag == 1) {
        //             busy = 0;
        //             break;
        //         }
        //         else {
        //             busy ++;
        //         }
        //         if (busy >= 1000*threadmaxruntime) {
        //             busy = 0;
        //             for (threadidit = threadid.begin(); threadidit != threadid.end(); threadidit ++) {
        //                 cout << threadtarget.at(*threadidit-1)->host << " overtime!" << endl;
        //                 // logout << threadtarget.at(*threadidit-1).host << " overtime!" << endl;
        //                 pthread_cancel(id[*threadidit-1]);
        //                 pthread_detach(id[*threadidit-1]);
        //                 threadfree.at(*threadidit-1) = true;
        //                 threadtimes.at(*threadidit-1) = 0;
        //                 pthread_mutex_unlock(&mutex);
        //                 //free(threadtarget.at(*threadidit-1));
        //             }
        //         }
        //         usleep(1000);
        //     }
        // }
        // in.close();
        // in.clear();
        // ofstream tempout2(outfilepath.c_str(), std::ios::app);
        // tempout2.close();
        // tempout2.clear();
        fclose(f);
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