#!/bin/sh
rootpath="/yun/resource_2017_1_1"
filename="R3_R2_7_left"
cp ${rootpath}/${filename}/log.txt ${rootpath}/Record/7_left_log.txt
cp ${rootpath}/${filename}/Total.txt ${rootpath}/Record/7_left_Total.txt
rm -rf ${rootpath}/${filename}/log.txt
rm -rf ${rootpath}/${filename}/Total.txt
mkdir ${rootpath}/${filename}_hex/
python handler2.py -i ${rootpath}/${filename}/ -o ${rootpath}/${filename}_hex/
python delete.py -f ${rootpath}/${filename}_hex/
# python transformpattern2.py -i pattern_origin/ -o pattern_hex/
mkdir ${rootpath}/${filename}_hex_result/
./dynamicAC -i ${rootpath}/${filename}_hex/ -o ${rootpath}/${filename}_hex_result/ -p pattern_hex/pattern.txt -w weight.txt
python delete.py -f ${rootpath}/${filename}_hex_result/
mkdir ${rootpath}/${filename}_result/
cp ${rootpath}/${filename}_hex_result/log.txt ${rootpath}/${filename}_result/log.txt
rm -rf ${rootpath}/${filename}_hex_result/log.txt
python recover.py -i ${rootpath}/${filename}_hex_result/ -o ${rootpath}/${filename}_result/
python delete.py -f ${rootpath}/${filename}_result/
# rm -rf ${rootpath}/${filename}_hex/
# rm -rf ${rootpath}/${filename}_hex_result/

