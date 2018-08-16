#include "Headers/dynamicAC.h"
#include "Headers/define.h"
#include "Headers/transform.h"
#include "Headers/readfile.h"
#include "Headers/dynamictool.h"
#include "Headers/matchthread.h"


bool haveothernextnode(Tree tempnode, int num) {
    for (int i = 0; i < ASCII; i ++) {
        if (tempnode->next[i] != NULL && i != num) {
            return true;
        }
    }
    return false;
}


void deletepattern(Tree root, string pattern) {
    Tree tempnode = root;
    vector<Tree> deletenode;
    int deletelength = 0;
    for (int i = 0; i < pattern.size();) {
        char ch1 = pattern[i ++];
        char ch2 = pattern[i ++];
        int num = hexchar2int(ch1, ch2);
        if ((tempnode = tempnode->next[num]) == NULL) {
            cout << "the pattern is not exist." << endl;
            return;
        }
        else {
            char ch3 = pattern[i];
            char ch4 = pattern[i + 1];
            int num2 = hexchar2int(ch3, ch4);
            if (i >= pattern.size()) {
                deletenode.push_back(tempnode);
                deletelength ++;
                break;
            }
            if (!haveothernextnode(tempnode, num2)) {
                deletenode.push_back(tempnode);
                deletelength ++;
            }
            else {
                deletelength = 0;
                deletenode.clear();
            }
        }
    }
    vector<Tree>::iterator it;
    char ch1 = deletenode.at(0)->inputchar[0];
    char ch2 = deletenode.at(0)->inputchar[1];
    int num = hexchar2int(ch1, ch2);
    deletenode.at(0)->par->next[num] = NULL;
    for (it = deletenode.begin(); it != deletenode.end(); it ++) {
        free((*it));
    }
}

void addpattern(Tree root, string pattern, int no) {
    Tree tempnode = root;
    Tree tempnode1 = NULL;
    //cout << "HERE1!" << endl;
    for (int i = 0; i < pattern.size(); i += 2) {
        char ch1 = pattern[i];
        char ch2 = pattern[i + 1];
        int num = hexchar2int(ch1, ch2);
        if (tempnode->next[num] == NULL) {
            tempnode1 = getNewNode();
            tempnode1->par = tempnode;
            strcpy(tempnode1->inputchar, pattern.substr(i, i+2).c_str());
            tempnode->next[num] = tempnode1;
            tempnode = tempnode1;
        }
        else {
            tempnode = tempnode->next[num];
        }
    }
    //cout << "HERE2!" << endl;
    tempnode->patterTag=1;
    tempnode->patterNo=no;
    //cout << "HERE3!" << endl;
    strcpy(tempnode->patternname, pattern.c_str());
}
