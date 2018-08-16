#include "Headers/dynamicAC.h"
#include "Headers/define.h"
#include "Headers/transform.h"
#include "Headers/readfile.h"
#include "Headers/dynamictool.h"


string string2hex(string const &s)
{
    char temp[30] = {'\0'};
    string ret;
    unsigned i = 0, j = 0;
    for (i = 0, j = 0; i != s.size(); ++i)
    {
        char hex[5] = {'\0'};
        sprintf(hex, "%#.2x ", (unsigned char)s[i]);
        temp[j ++] = hex[2];
        temp[j ++] = hex[3];
    }
    ret = temp;
    return ret.substr(0, i-1);
}

int hexchar2int(char ch1, char ch2) {
    int num1 = 0, num2 = 0;
    switch (ch1) {
        case '0': num1 = 0; break;
        case '1': num1 = 1; break;
        case '2': num1 = 2; break;
        case '3': num1 = 3; break;
        case '4': num1 = 4; break;
        case '5': num1 = 5; break;
        case '6': num1 = 6; break;
        case '7': num1 = 7; break;
        case '8': num1 = 8; break;
        case '9': num1 = 9; break;
        case 'a': num1 = 10; break;
        case 'b': num1 = 11; break;
        case 'c': num1 = 12; break;
        case 'd': num1 = 13; break;
        case 'e': num1 = 14; break;
        case 'f': num1 = 15; break;
        default : num1 = 0;
    }
    switch (ch2) {
        case '0': num2 = 0; break;
        case '1': num2 = 1; break;
        case '2': num2 = 2; break;
        case '3': num2 = 3; break;
        case '4': num2 = 4; break;
        case '5': num2 = 5; break;
        case '6': num2 = 6; break;
        case '7': num2 = 7; break;
        case '8': num2 = 8; break;
        case '9': num2 = 9; break;
        case 'a': num2 = 10; break;
        case 'b': num2 = 11; break;
        case 'c': num2 = 12; break;
        case 'd': num2 = 13; break;
        case 'e': num2 = 14; break;
        case 'f': num2 = 15; break;
        default: num2 = 0;
    }
    return (num1 * 16 + num2);
}

void transformpattern(char origin[][10], char transformed[][10], int length) {
    for (int i = 0; i <= length-1; i ++) {
        string s = origin[i];
        strcpy(transformed[i], string2hex(s).c_str());
    }
}
