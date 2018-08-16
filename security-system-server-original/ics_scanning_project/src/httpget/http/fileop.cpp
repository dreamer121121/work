#include "Headers/define.h"

int readFileList(char *basePath, vector<string> *filename)
{
    DIR *dir;
    struct dirent *ptr;
    char base[1000];

    if ((dir = opendir(basePath)) == NULL)
    {
        perror("Open dir error...");
        exit(1);
    }
    int i = 0;
    cout << i << endl;
    while ((ptr=readdir(dir)) != NULL)
    {
        if(strcmp(ptr->d_name,".")==0 || strcmp(ptr->d_name,"..")==0)
            continue;
        else if(ptr->d_type == 8) {
            char temp[1000] = {'\0'};
            sprintf(temp, "%s/%s", basePath, ptr->d_name);
            string path = temp;
            cout << path << endl;
            filename->push_back(ptr->d_name);
            i ++;
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
    cout << i << endl;
    closedir(dir);
    return 1;
}
