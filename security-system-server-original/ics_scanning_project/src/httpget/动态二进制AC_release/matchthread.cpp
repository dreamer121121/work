#include "Headers/dynamicAC.h"
#include "Headers/define.h"
#include "Headers/transform.h"
#include "Headers/readfile.h"
#include "Headers/dynamictool.h"
#include "Headers/matchthread.h"


int calpatternnum(Tree temproot) {
    int sum = 0;
    if (temproot->patterTag == 1) {
        sum ++;
    }
    for (int i = 0; i < ASIZE; i ++) {
        if (temproot->next[i] != NULL) {
            sum += calpatternnum(temproot->next[i]);
        }
    }
    return sum;
}

void handler(map<string, int> *successmap) {
    //if (rootnum == 0) {
        //cout << "root pattern number = " << calpatternnum(root) << endl;
    //}
    //else {
        //cout << "root1 pattern number = " << calpatternnum(root1) << endl;
    //}
    map<string, int>::iterator iter;
    iter = (*successmap).begin();
    for (; iter != (*successmap).end(); iter ++) {
        cout << "pattern : " << iter->first << " times : " << iter->second << endl;
    }
}


//void matchthread() {
void *matchthread(void* arg) {
    int max = 1000;
    int i = 0;
    while (true) {
        string message = getmessage("message.txt");
        map<string, int> *successmap = new map<string, int>();
        if (rootnum == 0) {
            //cout << "the matching thread is using root to match." << endl;
            pthread_mutex_lock(&mutex);
            threadrootnum = 0;
            pthread_mutex_unlock(&mutex);
            searchAC(root, (char*)message.c_str(), message.size(), successmap);
            //cout << root << endl;
            handler(successmap);
        }
        else {
            //cout << "the matching thread is using root1 to match." << endl;
            pthread_mutex_lock(&mutex);
            threadrootnum = 1;
            pthread_mutex_unlock(&mutex);
            searchAC(root1, (char*)message.c_str(), message.size(), successmap);
            handler(successmap);
        }
        free(successmap);
        //cout << "match pattern success!" << endl;
        if (i ++ >= max) {
            finish = true;
            break;
        }
    }
    cout << "The match thread has been finished." << endl;
    return arg;
}
