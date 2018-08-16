import datetime
import os
import platform
import random
import sqlite3

sep = '\\' if platform.system() == 'Windows' else '/'


def getTimeList(Number, Days, StartTime):
    TimeList = []
    avg = Number / Days  # 平均
    k = 0.41  # 斜率
    u = 0.23  # 误差

    for eachDay in range(Days):
        # rebuild function
        avg = Number / (Days - eachDay)
        b = avg - k / 2 * (Days - eachDay)  # 截距
        # caculate eachday's number
        eachDayNumber = random.randint(int((k * eachDay + b) * (1 - u)), int((k * eachDay + b) * (1 + u)))
        if eachDay == Days - 1:
            eachDayNumber = Number
        eachDayDel = datetime.timedelta(days=eachDay)
        eachDayTime = StartTime + eachDayDel
        for x in range(eachDayNumber):
            # rebuild hour minute and second
            eachDayTime = eachDayTime.replace(hour=random.randint(0, 23))
            eachDayTime = eachDayTime.replace(minute=random.randint(0, 59))
            eachDayTime = eachDayTime.replace(second=random.randint(0, 59))
            TimeList.append(eachDayTime)
        # rebuild Number
        Number = Number - eachDayNumber
    return TimeList


def getDirAllFileList(Dir):
    dir_list = []
    for root, dirs, files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root, file))
    return dir_list


f_in = input("input your file absolutely path\n")
f_in = open(f_in, "r", encoding='utf-8')
lines = f_in.readlines()
Number = len(lines) - 1
print(Number)
StartTime = datetime.datetime(2016, 8, 20, 12, 33, 44)
EndTime = datetime.datetime(2017, 1, 10, 13, 22, 33)
Days = int((EndTime - StartTime).days)
print(str(Days))
TimeList = getTimeList(Number, Days, StartTime)
conn = sqlite3.connect('db.sqlite3')
index = 0
for line in lines:
    if len(lines) < 10:
        continue
    ip, port, Country, Subdivisions, City, Lot, Lat = line.split("\t\t")
    if index >= len(TimeList):
        index = len(TimeList) - 1
    # conn.execute("insert into knowledgeBase_instance (name, ins_type, ip, city, country, lat, lon, port, timestamp) values('" + ip + "', 'Camera', '" + ip + "', '" + City + "', '" +  + ")")
    conn.execute(
        "insert into knowledgeBase_instance (name,ins_type,ip,city,country,lat,lon,port,timestamp) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
        ip, "Camera", ip, City, Country, Lat, Lon, port, TimeList[index].strftime("%Y-%m-%d %H:%M:%S")))
    index += 1
f_in.close()
"""
conn = sqlite3.connect('db.sqlite3')
conn.execute("insert into knowledgeBase_instance (name,ins_type,ip,city,country,lat,lon,port,timestamp) values('test','Camera','test','test','test','50','85','test','test')")
conn.commit()
conn.close()
"""
