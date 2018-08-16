#-*- coding: UTF-8 -*-
import string
import os,sys

base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('a'),ord('a')+6)]

def string2int(s):
    ret = ""
    for ch in s:
        ret += dec2hex(ord(ch))
    return ret


def dec2hex(num):
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 16)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])
    


s = "我是冯岩父亲"
ret = string2int(s)
print (ret)
