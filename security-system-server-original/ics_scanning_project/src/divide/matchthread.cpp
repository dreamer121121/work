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
    double evalution = 0;
    int num = 0, flag = 0;
    for (; iter != (*successmap).end(); iter ++) {
        evalution += weight[iter->first] * iter->second;
        if (iter->second == 1) {
            flag = 1;
        }
        num ++;
    }
    if ((*successmap).count("757365726e616d65") && (*successmap).count("70617373776f7264") && (*successmap).count("6c6f67696e")) {
        if ((*successmap).size() >= 4) {
            evalution = 1;
        }
        else {
            evalution = 0;
        }
    }
    else if ((*successmap).count("757365726e616d65") && (*successmap).count("70617373776f7264")) {
        if ((*successmap).size() >= 3) {
            evalution = 1;
        }
        else {
            evalution = 0;
        }
    }
    else if ((*successmap).count("6c6f67696e") && (*successmap).count("70617373776f7264")) {
        if ((*successmap).size() >= 3) {
            evalution = 1;
        }
        else {
            evalution = 0;
        }
    }
    else if ((*successmap).count("6c6f67696e") && (*successmap).count("757365726e616d65")) {
        if ((*successmap).size() >= 3) {
            evalution = 1;
        }
        else {
            evalution = 0;
        }
    }
    else {
        evalution = 0;
    }
    if (evalution >= 1) {
        if (flag == 0 && num == 1) {
            return;
        }
        ofstream out(outputfilename.c_str() + curfilename, ios::app);
        // out << "--------------------------------------------------" << endl;
        // out << "HOST: " + curhost + " PORT: " + to_string(curport) << endl;
        // out << "message:" << endl;
        // out << curmessage << endl;
        out << "--------------------------------------------------" << endl;
        out << "HOST: " + curhost + " PORT: " + to_string(curport) << endl;
        out << "Tag:" << endl;
        int haverecordscada = 0, haverecordipcamera = 0;
        for (iter = (*successmap).begin(); iter != (*successmap).end(); iter ++) {
            if (iter->first == "7363616461") {
                if (haverecordscada == 0) {
                    scadanum ++;
                    haverecordscada ++;
                }
            }
            else if (iter->first == "69702063616d657261" || iter->first == "6170702d77656273" || iter->first == "69702d63616d657261" || iter->first == "2d77656273" || iter->first == "776562736572766572") {
                if (haverecordipcamera == 0) {
                    ipcameranum ++;
                    haverecordipcamera ++;
                }
            }
            out << iter->first << " ";
        }
        totalnum ++;
        out << endl;
        out << "message:" << endl;
        out << curmessage << endl;
        out.close();
    }
}


//void matchthread() {
void *matchthread(void* arg) {
    //int max = 5000000;
    int i = 0;
    while (true) {
        // string message = getmessage("message.txt");
        string message = getnextmessage();
        if (message == "none") {
            break;
        }
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
        // cout << "match pattern success!" << endl;
        // if (i ++ >= max) {
        //     finish = true;
        //     break;
        // }
    }
    cout << "The match thread has been finished." << endl;
    ofstream logout((outputfilename + "log.txt").c_str());
    if (logout.is_open()) {
        logout << "scada num : " << scadanum << endl;
        logout << "ipcamera num : " << ipcameranum << endl;
        logout << "total num : " << totalnum << endl;
        logout.close();
    }
    finish = true;
    return arg;
}
