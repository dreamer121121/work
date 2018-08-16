#-*- coding:utf-8 -*-
import MySQLdb
import urllib2
import codecs
from bs4 import BeautifulSoup   
import sys
import json
import urllib
import getopt
import uuid
import common.settings as  SETTINGS
reload(sys)
sys.setdefaultencoding('utf8')


def main(argv):
    #result = []
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    
    ports = ['102', '502', '2404', '20000', '44818', '47808', '1911', '789', '9600', '1962', '20547', '5007']
    
    for sinport in ports:
        
        searchStr = 'port:%s' % sinport

        db_config = SETTINGS.DATABASE
        db = MySQLdb.connect(db_config["HOST"], db_config["USER"], db_config["PASSWORD"], db_config["NAME"])  # 数据库账号、密码
        #db = MySQLdb.connect("localhost", "root", "8571512411", "ics_scan")
        cursor = db.cursor()
        
        #searchStr = raw_input("search:")
        url = 'http://www.ditecting.com/index.php/home/result/index/query/' + urllib.quote(searchStr)
        #req = urllib2.Request(url, headers = header)
        req = urllib2.Request(url)
        #fname = raw_input("file_name:")

        #f = codecs.open(fname,'w','utf-8')
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response)

        totalNum = int(soup.find_all(style="color:green")[1].string)
        print 'total results: %d' % totalNum
        if totalNum%10 == 0:
            totalPage = int(totalNum/10)
        else:
            totalPage = int(totalNum/10) + 1
        #print 'total page:'+ str(totalPage)
        print 'total pages: %d' % totalPage
        for i in range(1, totalPage+1):
            print 'page:'+str(i)
            tempUrl = url +'/p/'+ str(i)+'.html'
            #req = urllib2.Request(tempUrl, headers = header)
            req = urllib2.Request(tempUrl)
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response)
            bannerStr = soup.find_all('xmp')
            contentStr = soup.find_all('p')
            otherStr = soup.find_all('span')
            otherj = 0 #register the array count
            bannerj = 0
            j = 0
            while j < len(contentStr):
                if contentStr[j].strong != None:
                    #ele = {}
                    ip = contentStr[j].strong.string
                    j = j+1
                    location = contentStr[j].get_text().split('Location ')[1]
                    country = MySQLdb.escape_string((location.split('   '))[0])
                    city = MySQLdb.escape_string((location.split('   '))[1])
                    j = j+1
                    service = contentStr[j].get_text()#这里的service（协议名）和instance表里面的service不一样
                    banner = MySQLdb.escape_string(bannerStr[bannerj].get_text())
                    bannerj = bannerj+1
                    while len(otherStr[otherj]['class']) < 2 or otherStr[otherj]['class'][1] != 'label-danger':
                        otherj = otherj+1
                    port = otherStr[otherj].get_text()
                    id = uuid.uuid1()
                    protocol = get_proto(port)
                    timeStr = otherStr[otherj-1].get_text()
                    timestamp = filter(unicode.isdigit, timeStr)
                    from_web = 'ditecting'
                    from_spider = 1
                    #result.append(ele)
                    #add to mysql
                    sql_find_location = "SELECT lat, lng, organization, as_num from knowledgeBase_iplocation where(ip = '%s')" % ip
                    located = cursor.execute(sql_find_location)
                    if located > 1:
                        print "more than one ip(primary key)"
                        j = j+1
                        continue
                    elif located == 1:#table iplocation has this ip
                        result = cursor.fetchone()
                        lat = result[0]
                        lon = result[1]
                        organization = result[2]
                        asn = result[3]
                    else:#new ip
                        addTo_ip_location = "INSERT INTO knowledgeBase_iplocation(ip, lat, lng) VALUES ('%s', '', '')" % ip
                        try:
                            cursor.execute(addTo_ip_location)
                            db.commit()
                        except:
                            print 'cannot insert to table knowledgeBase_iplocation\n' + addTo_ip_location
                            db.rollback()
                        lat = ''
                        lon = ''
                        organization = ''
                        asn = ''
                    sql_find = "SELECT * from knowledgeBase_instance where(ip = '%s')" % ip
                    count = cursor.execute(sql_find)
                    if count > 1:
                        print "ip has more than 1 register"
                    elif count == 1:#old 
                        pass#do nothing
                    else:
                        #new register
                        addTo_instance = "INSERT INTO knowledgeBase_instance(ip, asn, country, city, organization, timestamp, lat, lon, from_web, from_spider) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)" % (ip, asn, country, city, organization, timestamp, lat, lon, from_web, from_spider)
                        addTo_instanceport = "INSERT INTO knowledgeBase_instanceport(id, ip, port, banner, add_time, update_time, protocol) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, ip, port, banner, timestamp, timestamp, protocol)
                        try:
                            cursor.execute(addTo_instance)
                            cursor.execute(addTo_instanceport)
                            #cursor.execute("INSERT INTO knowledgeBase_instance(ip, asn, country, city, organization, timestamp, lat, lon, from_web, from_spider) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)" % (ip, asn, country, city, organization, timestamp, lat, lon, from_web, from_spider))
                            #cursor.execute("INSERT INTO knowledgeBase_instanceport(id, ip, port, banner, add_time, update_time, protocol) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, ip, port, banner, timestamp, timestamp, protocol))
                            db.commit()
                        except Exception, e:#这儿会输出错误和没有导致错误的sql语句
                            print e
                            print addTo_instance
                            print '\n ********************\n'
                            print addTo_instanceport
                            db.rollback()
                            exit()
                j = j+1
        #print json.dumps(result, encoding='utf-8', ensure_ascii=False, indent=4)
        #print >> f, json.dumps(result, encoding='utf-8', ensure_ascii=False, indent=4)
        #f.close()
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
    main(sys.argv[1:])