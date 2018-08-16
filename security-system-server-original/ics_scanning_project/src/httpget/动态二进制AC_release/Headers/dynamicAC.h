#ifndef DYNAMICAC_H_INCLUDED
#define DYNAMICAC_H_INCLUDED


#define ASCII 256
#endif // DYNAMICAC_H_INCLUDED
#include <queue>
#include <string>
#include <map>

using namespace std;

typedef struct node {
    struct node *next[ASCII];   /*该结点延伸的下一个结点，由于我们让两个16进制字符一组，所以一共代表了256个数字，next数组的对应位置存放该结点延伸的下一个对应的结点*/
    struct node *par;           /*该结点的父亲结点*/
    struct node *fail;          /*该结点的失败路径访问的结点*/
    char inputchar[2];          /*存放该结点的值，两个16进制字符*/
    int patterTag;              /*1表示该结点是否是一个模式串的尾节点*/
    int patterNo;               /*如果patterTag为1，记录下该模式串在模式串数组中的位置*/
    char patternname[100];
}*Tree, TreeNode;

TreeNode *getNewNode();
int  nodeToQueue(Tree root,queue<Tree> &myqueue);
Tree buildingTree();
int buildingFailPath(Tree root);
bool ifleafnode(Tree tmp);
void followfailure(Tree tmp, int i, Tree root);
int searchAC(Tree root, char* str, int len, map<string, int> *successmap);
int destory(Tree tree);
void startmatch(char *buff, int len, int successnum[]);
bool judge(int successnum[]);
