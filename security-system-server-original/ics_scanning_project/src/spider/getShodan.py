# -*- coding:utf-8 -*-
import time
import uuid
import common.settings as  SETTINGS

import MySQLdb
import shodan
import random

def main():
    #f = codecs.open('china.json','w','utf-8')
    db_config = SETTINGS.DATABASE
    db = MySQLdb.connect(db_config["HOST"], db_config["USER"], db_config["PASSWORD"], db_config["NAME"])#数据库账号、密码
    cursor = db.cursor()
    SHODAN_API_KEY = "DF7LYF16WVqSCW5C715egWBpnS03y6si"  # 见文档
    Sapi = shodan.Shodan(SHODAN_API_KEY)
    ports = ['102', '502', '2404', '20000', '44818', '47808', '1911', '789', '9600', '1962', '20547', '5007']  # 初步只进行了这样十二种协议的查询
    # ports = ['2404']
    portNum = 0
    while(portNum < len(ports)):
        sin_port = ports[portNum]
        portNum += 1
        searchStr = 'port:%s country:"CN"' % sin_port
        # 这里和shodan的输入框内容保持一致就可以了，可以自行更改这里是中国的上面的十二种协议
        # 要注意这里的country过滤里面要用CN而不能用China
        count = 0
        results = []
        try:
            print 'search for page amount'
            result = Sapi.search(searchStr, timeout=20)
            time.sleep(random.randint(5, 15))
            #print 'result: %s' % len(result)
            count = result['total']
            print 'Results found: %s' % count
            # f.write(json.dumps(result['matches'],indent=4))
        except Exception, e:
            print 'Error: %s' % e
            portNum -= 1
            time.sleep(random.randint(5, 15))
            continue

        if count % 100 == 0:
            pageNum = count / 100
        else:
            pageNum = count / 100 + 1
        # 返回的时候一次并不是一页，而是十页，也就是100条，所以要除以100看页数

        i = 1
        while(i <= pageNum):#循环的最后有一个i自增操作
            try:
                print 'search for page: %s' % i
                result = Sapi.search(searchStr, page=i, timeout=50)
                time.sleep(random.randint(5,15))
                print 'finish Page: %s' % i
                # results = results + result['matches']
            except Exception, e:
                print 'Error: %s' % e
                time.sleep(random.randint(5, 15))
                continue
            for ele in result['matches']:
                if not ele.has_key('asn'):
                    ele['asn'] = ''
                if not ele.has_key('org'):
                    ele['org'] = ''
                if not ele.has_key('isp'):
                    ele['isp'] = ''
                if not ele.has_key('os'):
                    ele['os'] = ''
                # name = uuid.uuid1()
                # instance_id = name
                # print 'mark5'
                id = uuid.uuid1()
                ip = ele['ip_str']
                if ele['location']['city'] == None:
                    ele['location']['city'] = ''
                city = escape_string(ele['location']['city'])
                country = escape_string(ele['location']['country_name'])
                asn = escape_string(ele['asn'])
                lat = escape_string(ele['location']['latitude'])
                lon = escape_string(ele['location']['longitude'])
                os = escape_string(ele['os'])
                protocol = escape_string(get_proto(sin_port))
                port = escape_string(ele['port'])
                banner = escape_string(ele['data'])
                organization = escape_string(ele['org'])
                isp = escape_string(ele['isp'])
                timestamp = escape_string(ele['timestamp'])
                from_spider = 1
                from_web = "shodan"
                sql_find = "SELECT from_scan, from_web from knowledgeBase_instance where ip = '%s' " % ip
                count = cursor.execute(sql_find)
                # print 'mark6'
                if count > 1:
                    print "ip %s has more than 1 register" % ip
                    continue
                elif count == 1:  # old
                    result = cursor.fetchone()
                    if result[0] == 1:  # from_scan
                        addTo_instance = "update knowledgeBase_instance set ip = '%s', asn = '%s', country = '%s', city = '%s', organization = '%s', isp = '%s',  update_time = '%s', lat = '%s', lon = '%s', os = '%s', from_web = '%s', from_spider = %d where ip = '%s'" % (
                        ip, asn, country, city, organization, isp, timestamp, lat, lon, os, from_web, from_spider, ip)
                        addTo_instanceport = "update knowledgeBase_instanceport set ip = '%s', port = '%s', update_time = '%s', protocol = '%s' where ip = '%s' AND port = '%s'" % (
                        ip, port, timestamp, protocol, ip, port)
                    else:
                        addTo_instance = "update knowledgeBase_instance set ip = '%s', asn = '%s', country = '%s', city = '%s', organization = '%s', isp = '%s',  update_time = '%s', lat = '%s', lon = '%s', os = '%s', from_web = '%s', from_spider = %d where ip = '%s'" % (
                        ip, asn, country, city, organization, isp, timestamp, lat, lon, os, from_web, from_spider, ip)
                        addTo_instanceport = "update knowledgeBase_instanceport set ip = '%s', port = '%s', banner = '%s', update_time = '%s', protocol = '%s' where ip = '%s' AND port = '%s'" % (
                        ip, port, banner, timestamp, protocol, ip, port)
                else:  # count=0
                    addTo_instance = "INSERT INTO knowledgeBase_instance(ip, asn, country, city, organization, isp,  timestamp, lat, lon, os, from_web, from_spider) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)" % (
                    ip, asn, country, city, organization, isp, timestamp, lat, lon, os, from_web, from_spider)
                    addTo_instanceport = "INSERT INTO knowledgeBase_instanceport(id, ip, port, banner, add_time, update_time, protocol) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                    id, ip, port, banner, timestamp, timestamp, protocol)
                    # exit()
                # print 'mark7'
                try:
                    cursor.execute(addTo_instance)
                    cursor.execute(addTo_instanceport)
                    db.commit()
                except Exception, e:
                    print addTo_instance
                    print addTo_instanceport
                    db.rollback()
                    print "ERROR: %s" % e
            i += 1 
    db.close()

def get_proto(x):
    return {
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
        '5007': 'MELSEC-Q'
    }[x]

def escape_string(str):
    retStr = ''
    try:
        retStr = MySQLdb.escape_string(str)
    except Exception, e:
        retStr = str
    return retStr

if __name__ == "__main__":
    main()
