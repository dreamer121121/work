#include "Headers/define.h"



using namespace std;



void u_alarm_handler() {
    cout << "!!!!!!!!!!!!!!!!!!!!" <<endl;
}

/**
    create client
*/
int http_tcpclient_create(){
    int socket_fd;
    if((socket_fd = socket(AF_INET,SOCK_STREAM,0)) == -1){
        return -1;
    }
    return socket_fd;
}
/**
    connect server
*/
int http_tcpclient_connect(int socket_fd, char* host, int port, struct hostent *he, struct sockaddr_in *server_addr) {
    //cout << "http_tcpclient_connect start" << endl;
    //cout << host << port << socket_fd << endl;
    if (socket_fd == -1) {
        return -1;
    }
    if((he = gethostbyname(host))==NULL){
        return -1;
    }
    server_addr->sin_family = AF_INET;
    server_addr->sin_port = htons(port);
    server_addr->sin_addr = *((struct in_addr *)he->h_addr);
    //cout << socket_fd << " " << host << " :" << port << endl;

    /*fd_set rfd;
    struct timeval timeout;
    FD_ZERO(&rfd);
    timeout.tv_sec = 5;
    timeout.tv_usec = 0;
    u_long ul=1;
    ioctl(socket_fd,FIONBIO,&ul);
    connect(socket_fd, (struct sockaddr *)server_addr,sizeof(struct sockaddr));
    FD_SET(socket_fd,&rfd);
    int ret = select(0, 0, &rfd, 0, &timeout);
    if(ret <= 0) {
        return -1;
    }
    else {
        ul = 0;
        ioctl(socket_fd,FIONBIO,&ul);
    }*/


    if(connect(socket_fd, (struct sockaddr *)server_addr,sizeof(struct sockaddr)) == -1) {

        return -1;
    }


    //cout << "http_tcpclient_connect finish" << endl;
    return socket_fd;
}
/**
    close connection
*/
void http_tcpclient_close(int socket){
    close(socket);
}

/**
    send message
*/
int http_tcpclient_send(int socket,char *buff,int size){
    int sent=0,tmpres=0;
    //cout << "http_tcpclient_send start" << endl;
    while(sent < size){
        tmpres = send(socket,buff+sent,size-sent,0);
        if(tmpres == -1){
            return -1;
        }
        sent += tmpres;
    }
    //cout << "httptcp_client_send finish" << endl;
    return sent;
}


/**
    receive message
*/
int http_tcpclient_recv(int socket, char buff[]){
    int i = 0;
    int res = 0;
    int messagelength = 0;
    //cout << "http_tcpclient_recv start" << endl;
    char lpbuff[BUFFER_SIZE*4] = {'\0'};
    int nNetTimeout=5000;
    setsockopt(socket, SOL_SOCKET, SO_SNDTIMEO, (char*)&nNetTimeout, sizeof(int));

    /*while ((res = recv(socket, lpbuff, BUFFER_SIZE*4, 0)) > 0) {
        cout << res << endl;
        strcat(buff, lpbuff);
        cout << lpbuff <<endl;
        messagelength += res;
        i ++;
        lpbuff[BUFFER_SIZE*4] = {'\0'};
        if (res < BUFFER_SIZE*4) {
            break;
        }
    }*/


    // if ((res = recv(socket, lpbuff, BUFFER_SIZE*4, 0)) > 0) {
    //     cout << res << endl;
    //     strcat(buff, lpbuff);
    //     //cout << lpbuff <<endl;
    //     messagelength += res;
    //     i ++;
    //     lpbuff[BUFFER_SIZE*4] = {'\0'};
    // }
    // if (res < BUFFER_SIZE*4) {
    //     //cout << "http_tcpclient_recv finish" << endl;
    //     return messagelength;
    // }
    // if ((res = recv(socket, lpbuff, BUFFER_SIZE*4, 0)) > 0) {
    //     cout << "[**]size is too large to receive." << endl;
    //     return -1;
    // }
    // if (i == 0) {
    //     return -1;
    // }

    if ((res = recv(socket, lpbuff, BUFFER_SIZE*4, 0)) > 0) {
        //cout << res << endl;
        strcat(buff, lpbuff);
        //cout << lpbuff <<endl;
        messagelength += res;
        //i ++;
        //lpbuff[BUFFER_SIZE*4] = {'\0'};
    }
    else {
        return -1;
    }
    //cout << "http_tcpclient_recv finish" << endl;
    return messagelength;
}


int http_post(char *host, int port, int socket_fd, char *post_str, struct hostent *he, struct sockaddr_in *server_addr, char buff[BUFFER_MAX]){

    char file[BUFFER_SIZE] = {'\0'};
    char sendbuf[BUFFER_SIZE*4] = {'\0'};
    if(!host || !post_str){
        printf("[**]failed!\n");
        return -1;
    }
    sprintf(sendbuf, HTTP_POST, file, host, port, strlen(post_str), post_str);

    if(http_tcpclient_connect(socket_fd, host, port, he, server_addr) == -1) {
        return -1;
    }

    if(http_tcpclient_send(socket_fd, sendbuf, strlen(sendbuf)) < 0){
        printf("http_tcpclient_send failed..\n");
        return -1;
    }

    if (http_tcpclient_recv(socket_fd, buff) == -1) {
        cout << "http_tcpclient_recv failed.." << endl;
        return -1;
    }


    return 0;
}

int http_get(char *host, int port, int socket_fd, struct hostent *he, struct sockaddr_in *server_addr, char buff[BUFFER_MAX])
{
    int messagelength = 0;
    char file[BUFFER_SIZE] = {'\0'};
    char sendbuf[BUFFER_SIZE*4] = {'\0'};
    //cout << "http_get start" << endl;
    if(!host){
        printf("      failed!\n");
        return -1;
    }
    if(http_tcpclient_connect(socket_fd, host, port, he, server_addr) == -1) {
        return -1;
    }
    sprintf(sendbuf, HTTP_GET, file, host, port);
    if(http_tcpclient_send(socket_fd, sendbuf, strlen(sendbuf)) < 0){
        printf("http_tcpclient_send failed..\n");
        return -1;
    }
    if ((messagelength = http_tcpclient_recv(socket_fd, buff)) == -1) {
        cout << "http_tcpclient_recv failed.." << endl;
        return -1;
    }
    //cout << "http_get finish" << endl;
    return messagelength;
}