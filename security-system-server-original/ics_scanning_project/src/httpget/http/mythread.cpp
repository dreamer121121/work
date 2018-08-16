#include "Headers/define.h"
#include <exception>


void* mythread(void * arg) {
    int socket_fd = -1;
    int messagelength = 0;
    int thisthreadid = *(int *)arg;
    struct target tar = *(threadtarget.at(thisthreadid-1));
    struct hostent *he;
    struct sockaddr_in *server_addr;
    string outfilename = threadoutfile.at(thisthreadid-1);
    char buff[BUFFER_MAX] = {'\0'};
    try {
    //cout << tar.host <<endl;
    socket_fd = http_tcpclient_create();
    //cout << "tcpclient create success" << endl;
    if(socket_fd < 0){
        // cout << "host: " << tar.host << " port: " << tar.port << "[**]http_tcpclient_create failed." << endl;
        // logout << "host: " << tar.host << " port: " << tar.port << "[**]http_tcpclient_create failed." << endl;
        pthread_mutex_lock(&mutex2);
        free(arg);
        threadfree.at(thisthreadid - 1) = true;
        pthread_detach(pthread_self());
        pthread_mutex_unlock(&mutex2);
        return NULL;
    }
    he = (struct hostent*)malloc(sizeof(struct hostent));
    server_addr = (struct sockaddr_in*)malloc(sizeof(struct sockaddr_in));
    if (he == NULL || server_addr == NULL) {
        cout << "can't alloc memory!" << endl;
        pthread_mutex_lock(&mutex2);
        free((void*)he);
        free((void*)server_addr);
        http_tcpclient_close(socket_fd);
        free(arg);
        threadfree.at(thisthreadid - 1) = true;
        pthread_detach(pthread_self());
        pthread_mutex_unlock(&mutex2);
        return NULL;
    }
    if ((messagelength = http_get(tar.host, tar.port, socket_fd, he, server_addr, buff)) == -1) {
        // cout << "host: " << tar.host << " port: " << tar.port << " [**]http_get failed" << endl;
        // logout << "host: " << tar.host << " port: " << tar.port << "[**]http_get failed" << endl;
        pthread_mutex_lock(&mutex2);
        free((void*)he);
        free((void*)server_addr);
        http_tcpclient_close(socket_fd);
        free(arg);
        threadfree.at(thisthreadid - 1) = true;
        pthread_detach(pthread_self());
        pthread_mutex_unlock(&mutex2);
        return NULL;
    }
    //cout << "http_get success" << endl;
    pthread_mutex_lock(&mutex);
    char s[BUFFER_MAX] = {'\0'};
    sprintf(s, "HOST: %s PORT: %d\r\nmessage:\r\n%s\r\n", tar.host, tar.port, buff);
    //cout << outfilename << endl;
    // ofstream out(outfilename, std::ios::app);
    // if (!out.is_open()) {
    //     open((char*)outfilename.c_str(), (O_CREAT|O_WRONLY|O_TRUNC));
    // }
    // out << "--------------------------------------------------" << endl;
    // out << s;
    // out.close();
    // out.clear();
    FILE *f;
    f = fopen((char*)(outfilename.c_str()), "a+");
    if (f == NULL) {
        cout << "host: " << tar.host << " port: " << tar.port << " open file failed!" << endl;
        // logout << "host: " << tar.host << " port: " << tar.port << "[**]http_get failed" << endl;
        pthread_mutex_lock(&mutex2);
        free((void*)he);
        free((void*)server_addr);
        http_tcpclient_close(socket_fd);
        free(arg);
        threadfree.at(thisthreadid - 1) = true;
        pthread_detach(pthread_self());
        pthread_mutex_unlock(&mutex2);
        return NULL;
    }
    fprintf(f, "--------------------------------------------------\n");
    fprintf(f, "%s\n", s);
    fclose(f);

    free((void*)he);
    free((void*)server_addr);
    http_tcpclient_close(socket_fd);
    //cout << thisthreadid << endl;
    // cout << "host: " << tar.host << " port: " << tar.port << " success!!!" << endl;
    // logout << "host: " << tar.host << " port: " << tar.port << " success!!!" << endl;
    successnum ++;
    pthread_mutex_unlock(&mutex);
    free(arg);
    pthread_mutex_lock(&mutex2);
    //free(threadtarget.at(thisthreadid-1));
    threadfree.at(thisthreadid - 1) = true;
    pthread_detach(pthread_self());
    pthread_mutex_unlock(&mutex2);
    return NULL;
    } catch(exception e) {
        pthread_mutex_unlock(&mutex);
        free(arg);
        pthread_mutex_lock(&mutex2);
        //free(threadtarget.at(thisthreadid-1));
        threadfree.at(thisthreadid - 1) = true;
        pthread_detach(pthread_self());
        pthread_mutex_unlock(&mutex2);
        return NULL;
    }
}
