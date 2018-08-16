#-*- coding:utf-8 -*-
import time
import random
import MySQLdb
import uuid

import datetime
from zoomeye import zoomeye
import common.settings as  SETTINGS

def main():
    day = datetime.datetime.now().day
    user_num = len(SETTINGS.ZOOMEYE_USER)
    username = SETTINGS.ZOOMEYE_USER[day%user_num]["username"]
    password = SETTINGS.ZOOMEYE_USER[day%user_num]["password"]
    print (username, password)

    db_config = SETTINGS.DATABASE
    db = MySQLdb.connect(db_config["HOST"], db_config["USER"], db_config["PASSWORD"], db_config["NAME"])  # 数据库账号、密码
    #db = MySQLdb.connect("localhost", "root", "8571512411", "ics_scan")
    cursor = db.cursor()
        
    #ports = ['102', '502', '2404', '20000', '44818', '47808', '1911', '789', '9600', '1962', '20547', '5007']
    ports = ['102', '20000', '47808', '1911', '789', '9600', '20547', '5007']
    #ports = ['102']
    #和协议种类相关，可以自行更改
    for sin_port in ports:
        time.sleep(random.randint(0, 9))

        #searchString = raw_input("search:")
        #fname = raw_input("fileName:")
        searchString = 'port:' + sin_port + ' country:china'#中国的，这里可以更改，和zoomeye网站提供的搜索内容一致即可
        #fname = sin_port + '.json'
        #f = open(fname,'w')
        print "search: %s" % searchString
        
        z = zoomeye.Zoomeye(username, password)
        z.search(searchString)
        print 'total results: %d' % z.info['total']

        totalNum = z.info['total']*0.3 #can only get 30% of the results
        #只能获得到结果的30%，且最多1000页
        #totalNum = z.info['total']
        print '30 percents results: %d' % totalNum
        
        if totalNum%10 == 0:
            totalPage = int(totalNum/10)
        else:
            totalPage = int(totalNum/10) + 1
        print 'total pages: %d' % totalPage
        if totalPage > 1000:
            totalPage = 1000


        zz = zoomeye.Zoomeye(username, password)#zoomeye的账号、密码
        zz.search(searchString, pages = totalPage)

        for ele in zz.results:
            #name = uuid.uuid1()
            #instance_id = name
            id = uuid.uuid1()
            ip = ele['ip']
            if ip.find('*') != -1:#ip中包含*号
                continue
            city = ele['geoinfo']['city']['names']['en']
            country = ele['geoinfo']['country']['names']['en']
            continent = ele['geoinfo']['continent']['names']['en']
            #continent => instance
            asn = ele['geoinfo']['asn']
            lat = ele['geoinfo']['location']['lat']
            lon = ele['geoinfo']['location']['lon']
            isp = ele['geoinfo']['isp']
            organization = ele['geoinfo']['organization']
            hostname = ele['portinfo']['hostname']
            #hostname => instance
            #service = ele['portinfo']['service']
            app = ele['portinfo']['app']
            extrainfo = ele['portinfo']['extrainfo']
            version = ele['portinfo']['version']
            #app extrainfo version => instance
            os = ele['portinfo']['os']
            port = ele['portinfo']['port']
            banner = ele['portinfo']['banner']
            timestamp = ele['timestamp']
            protocol = get_proto(sin_port)
            from_spider = 1
            from_web = "zoomeye"
            sql_find = "SELECT from_scan, from_web from knowledgeBase_instance where(ip = '%s')" % ip
            count = cursor.execute(sql_find)
            if count > 1:
                print "ip has more than 1 register"
                #由于ip不是主键（但是同一个ip只能有一个），在这里进行了一个对数量的判断，当有多个ip相同时，会输出这一句，但是程序不会停止运行，会continue
                continue
            elif count == 1: #old register
            #count=1，说明数据库中之前就存在了相同的ip的信息，这里就需要update，而不是insert
            #再次说明，这个判断是很有必要的，因为ip不是主键！主键是uuid！uuid每次都不同，所以需要进行人为比对，而不能通过主键判断
                result = cursor.fetchone() #only one register
                #取出该条ip的信息，取出内容（见上面的sql_find语句）包括from_scan(result[0])和from_web(result[1])
                if result[0] == 1:#from_scan 
                #说明是自己扫描的
                    addTo_instance = "update knowledgeBase_instance set ip = '%s', country = '%s', city = '%s', continent = '%s', asn = '%s', organization = '%s', isp = '%s',  update_time = '%s', lat = '%s', lon = '%s', os = '%s', hostname = '%s', app = '%s', extrainfo = '%s', version = '%s', from_web = '%s', from_spider = %dwhere ip = '%s'" % (ip, country, city, continent, asn, organization, isp,  timestamp, lat, lon, os, hostname, app, extrainfo, version, from_web, from_spider, ip)
                    addTo_instanceport = "update knowledgeBase_instanceport set ip = '%s', port = '%s', update_time = '%s', protocol = '%s' where ip = '%s' AND port = '%s'" % (ip, port, timestamp, protocol, ip, port)
                    #在这里需要注意一点，在update扫描的数据时，不要更改扫描的内容，现在，扫描只有一个banner？和timestamp？所以banner内容就没有update
                elif result[1] == 'shodan':
                    #shodan的优先级更高，所以只update一些shodan没有的内容
                    addTo_instance = "update knowledgeBase_instance set continent = '%s', hostname = '%s', app = '%s', extrainfo = '%s', version = '%s' where ip = '%s'" % (continent, hostname, app, extrainfo, version, ip)
                    addTo_instanceport = "show tables"#no use
                    #这里不需要addTo_instanceport，但是这里的addTo_instanceport写了一个“show tables”，别删了，因为删了之后，由于之后会执行“cursor.execute(addTo_instanceport)”，会出问题，其实也可以在后面“cursor.execute”处进行一个判断，
                else:#zoomeye or ditecting
                #zoomeye（自身的）或者是谛听的，就全部update一次
                    addTo_instance = "update knowledgeBase_instance set ip = '%s', country = '%s', city = '%s', continent = '%s', asn = '%s', organization = '%s', isp = '%s',  update_time = '%s', lat = '%s', lon = '%s', os = '%s', hostname = '%s', app = '%s', extrainfo = '%s', version = '%s', from_web = '%s', from_spider = %d where ip = '%s'" % (ip, country, city, continent, asn, organization, isp,  timestamp, lat, lon, os, hostname, app, extrainfo, version, from_web, from_spider, ip)
                    addTo_instanceport = "update knowledgeBase_instanceport set ip = '%s', port = '%s', banner = '%s', update_time = '%s', protocol = '%s' where ip = '%s' AND port = '%s'" % (ip, port, banner, timestamp, protocol, ip, port)
            else: #new register
            #count=0，说明数据库之前没有，就需要insert
                addTo_instance = "INSERT INTO knowledgeBase_instance(ip, country, city, continent, asn, organization, isp, timestamp, lat, lon, os, hostname, app, extrainfo, version, from_web, from_spider) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)" % (ip, country, city, continent, asn, organization, isp, timestamp, lat, lon, os, hostname, app, extrainfo, version, from_web, from_spider)
                addTo_instanceport = "INSERT INTO knowledgeBase_instanceport(id, ip, port, banner, add_time, update_time, protocol) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, ip, port, banner, timestamp, timestamp, protocol)
            #continent hostname app extrainfo version
            try:
                cursor.execute(addTo_instance)
                cursor.execute(addTo_instanceport)
                db.commit()
            except:
                db.rollback()
        #f.write(json.dumps(zz.results,indent=4))
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

if __name__ == "__main__":
    main()
