#-*- coding:utf-8 -*-
import json
import MySQLdb
import codecs
import sys
import uuid
import time
import getopt
import os

def getDirAllFileList(Dir) :
    dir_list = []
    for root,dirs,files in os.walk(Dir):
        for file in files:
            dir_list.append(os.path.join(root,file))
    return dir_list

def getPTC(port) :
    NSE2PORT = {
        '102': 'Siemens S7',
        '502': 'Modbus',
        '2404': 'IEC 60870-5-104',
        '20000': 'DNP3',
        '44818': 'EtherNet/IP',
        '47808': 'BACnet',
        '1911': 'Tridium Niagara Fox',
        '789': 'Crimson V3',
        '9600': 'OMRON FINS',
        '1962': 'PCWorx',
        '20547': 'ProConOs',
        '5007': 'MELSEC-Q' ,
        
        '445' : 'Stuxnet',
        '10001' : 'ATG' ,
        '2455' : 'Codesys',
        '137' : 'Siemens-WINCC',
        '4800' : 'Moxa',
        '5006': 'MELSEC-Q-U',
        '20000' : 'DNP3',
        '2222' : 'CSPV4'
    }
    NSE = NSE2PORT.get(port, "ELSE")
    return NSE

def insert(db, cursor, ip, port, banner) :
    port = str(port)
    #name = uuid.uuid1()
    #instance_id = name
    id = uuid.uuid1()
    protocol = getPTC(port)
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    from_scan = 1
    sql_find = "SELECT * from knowledgeBase_instance where(ip = '%s')" % ip
    count = cursor.execute(sql_find)
    if count != 0: #old
        addTo_instance = "update knowledgeBase_instance set ip = '%s', update_time = '%s', from_scan = %d where ip = '%s'" % (ip, timestamp, from_scan, ip)
        addTo_instanceport = "update knowledgeBase_instanceport set ip = '%s', port = '%s', banner = '%s', update_time = '%s', protocol = '%s' where ip = '%s' AND port = '%s'" % (ip, port, banner, timestamp, protocol, ip, port)
    else:
        addTo_instance = "INSERT INTO knowledgeBase_instance(ip, timestamp, from_spider) VALUES ('%s', '%s', %d)" % (ip, timestamp, from_scan)
        addTo_instanceport = "INSERT INTO knowledgeBase_instanceport(id, ip, port, banner, add_time, update_time, protocol) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, ip, port, banner, timestamp, timestamp, protocol)
    try:
        #cursor.execute(addTo_t_device)
        #cursor.execute(addTo_t_device_port)
        #cursor.execute(addTo_t_ip_location)
        cursor.execute(addTo_instance)
        cursor.execute(addTo_instanceport)
        db.commit()
    except:
        db.rollback()

def usageINS() :
    print ("-i : in_path")
    
if __name__ == "__main__" :
    opts, args = getopt.getopt(sys.argv[1: ], "i:h:u:p:n:")
    db_config = {}
    for op,value in opts :
        if op == "-i" :
            in_path = value
        elif op == "-h" :
            db_config["HOST"] = value
        elif op == "-u":
            db_config["USER"] = value
        elif op == "-p":
            db_config["PASSWORD"] = value
        elif op == "-n":
            db_config["NAME"] = value

    All_File_Path = getDirAllFileList(in_path)
    db = MySQLdb.connect(db_config["HOST"], db_config["USER"], db_config["PASSWORD"], db_config["NAME"])
    cursor = db.cursor()
    #insert(db, cursor, ip, port, banner)
    for each_File in All_File_Path :
        f_each = open(each_File)
        Lines = f_each.read()
        f_each.close()
        Lines = Lines.split("--------------------------------------------------\n")
        for EachPart in Lines :
            #print EachPart
            if len(EachPart) < 35 :
                continue
            PartLines = EachPart.split("\n")
            ip = PartLines[0].split(" ")[2].split(".")
            if len(ip) < 4 :
                continue
            ip = ip[0] + '.' + ip [1] + '.' + ip[2] + '.' + ip[3]
            port = int(PartLines[3].split('/')[0])
            banner = ''
            for i in range(4, 30) :
                if i >= len(PartLines) :
                    break
                banner = banner + PartLines[i][2:] + "\n"
            print ("---\nip : %s\nport : %d\nbanner : %s" % (ip, port, banner))
            insert(db, cursor, ip, port, banner)            
