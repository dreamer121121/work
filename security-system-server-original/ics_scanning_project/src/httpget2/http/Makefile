httpget: main.o mythread.o client.o fileop.o
	g++ -Wall -fexceptions -g -L /usr/include/ -I /root/http/ -o httpget main.o mythread.o client.o fileop.o -lpthread -std=c++11
main.o: main.cpp Headers/define.h Headers/fileop.h Headers/client.h Headers/mythread.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/http/ -lpthread -c main.cpp -o main.o
mythread.o: mythread.cpp Headers/define.h Headers/fileop.h Headers/client.h Headers/mythread.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/http/ -lpthread -c mythread.cpp -o mythread.o
client.o: client.cpp Headers/define.h Headers/fileop.h Headers/client.h Headers/mythread.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/http/ -lpthread -c client.cpp -o client.o
fileop.o: fileop.cpp Headers/define.h Headers/fileop.h Headers/client.h Headers/mythread.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/http/ -lpthread -c fileop.cpp -o fileop.o
clean:
	-rm httpget main.o mythread.o client.o fileop.o

