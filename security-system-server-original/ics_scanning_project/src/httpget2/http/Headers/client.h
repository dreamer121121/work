#ifndef CLIENT_H_INCLUDED
#define CLIENT_H_INCLUDED



#endif // CLIENT_H_INCLUDED

#define BUFFER_SIZE 1024
#define HTTP_POST "POST /%s HTTP/1.1\r\nHOST: %s:%d\r\nAccept: */*\r\n"\
    "Content-Type:application/octet-stream/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s"
#define HTTP_GET "GET /%s HTTP/1.1\r\nHOST: %s:%d\r\nAccept: */*\r\n\r\nContent-Type:application/octet-stream\r\n\r\n"
#define BUFFER_LENGTH 100
#define BUFFER_MAX 65535
#define ASIZE 256
#define MAX(a, b)  (((a) > (b)) ? (a) : (b))
#define ITEMMAX 1000
#define patternnum 4
#define ASCII 256
#define patternlength 100


int http_tcpclient_create();
int http_tcpclient_connect(int socket_fd, char* host, int port, struct hostent *he, struct sockaddr_in *server_addr);
void http_tcpclient_close(int socket);
int http_tcpclient_send(int socket,char *buff,int size);
int http_tcpclient_recv(int socket, char buff[]);
int http_post(char *host, int port, int socket_fd, char *post_str, struct hostent *he, struct sockaddr_in *server_addr, char buff[BUFFER_MAX]);
int http_get(char *host, int port, int socket_fd, struct hostent *he, struct sockaddr_in *server_addr, char buff[BUFFER_MAX]);
