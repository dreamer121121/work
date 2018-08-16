dynamicAC: main.o matchthread.o readfile.o transform.o dynamicAC.o dynamictool.o
	g++ -Wall -fexceptions -g -L /usr/include/ -I /root/dynamicAC/ -o dynamicAC main.o matchthread.o readfile.o transform.o dynamicAC.o dynamictool.o -lpthread -std=c++11
main.o: main.cpp Headers/define.h Headers/dynamicAC.h Headers/dynamictool.h Headers/matchthread.h Headers/readfile.h Headers/transform.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/dynamicAC/ -lpthread -c main.cpp -o main.o
matchthread.o: matchthread.cpp Headers/define.h Headers/dynamicAC.h Headers/dynamictool.h Headers/matchthread.h Headers/readfile.h Headers/transform.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/dynamicAC/ -lpthread -c matchthread.cpp -o matchthread.o
readfile.o: readfile.cpp Headers/define.h Headers/dynamicAC.h Headers/dynamictool.h Headers/matchthread.h Headers/readfile.h Headers/transform.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/dynamicAC/ -lpthread -c readfile.cpp -o readfile.o
transform.o: transform.cpp Headers/define.h Headers/dynamicAC.h Headers/dynamictool.h Headers/matchthread.h Headers/readfile.h Headers/transform.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/dynamicAC/ -lpthread -c transform.cpp -o transform.o
dynamicAC.o: dynamicAC.cpp Headers/define.h Headers/dynamicAC.h Headers/dynamictool.h Headers/matchthread.h Headers/readfile.h Headers/transform.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/dynamicAC/ -lpthread -c dynamicAC.cpp -o dynamicAC.o
dynamictool.o: dynamictool.cpp Headers/define.h Headers/dynamicAC.h Headers/dynamictool.h Headers/matchthread.h Headers/readfile.h Headers/transform.h
	g++ -Wall -fexceptions -g -std=c++11 -L /usr/include/ -I /root/dynamicAC/ -lpthread -c dynamictool.cpp -o dynamictool.o
clean:
	-rm dynamicAC main.o matchthread.o readfile.o transform.o dynamicAC.o dynamictool.o