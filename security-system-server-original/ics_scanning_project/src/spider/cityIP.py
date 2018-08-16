import MySQLdb
import urllib2
import codecs
from bs4 import BeautifulSoup   
import sys
import json
import urllib
from zoomeye import zoomeye
import json
reload(sys)
sys.setdefaultencoding('utf8')

'''
    BJ    beijing           GD    guangdong
    SD    shandong          ZJ    zhejiang
    JS    jiangsu           SH    shanghai
    LN    liaoning          SC    sichuang
    HA    henan             HB    hubei
    FJ    fujian            HN    hunan
    HE    hebei             CQ    chongqing
    SX    shanxi            JX    jiangxi
    SN    shaanxi           AH    anhui
    HL    heilongjiang      GX    guangxi
    JL    jilin             YN    yunnan
    TJ    tianjin           NM    neimenggu
    XJ    xinjiang          GS    gansu
    GZ    guizhou           HI    hainan
    NX    ningxia           QH    qinghai
    XZ    xizang            HK    hongkong
'''


def main():
    cities = {
    'BJ':'beijing',
    'GD':'guangdong',
    'SD':'shandong',
    'ZJ':'zhejiang',
    'JS':'jiangsu',       
    'SH':'shanghai',
    'LN':'liaoning',    
    'SC':'sichuang',
    'HA':'henan',        
    'HB':'hubei',
    'FJ':'fujian',     
    'HN':'hunan',
    'HE':'hebei',         
    'CQ':'chongqing',
    'SX':'shanxi',        
    'JX':'jiangxi',
    'SN':'shaanxi',        
    'AH':'anhui',
    'HL':'heilongjiang',   
    'GX':'guangxi',
    'JL':'jilin',          
    'YN':'yunnan',
    'TJ':'tianjin',        
    'NM':'neimenggu',
    'XJ':'xinjiang',       
    'GS':'gansu',
    'GZ':'guizhou',        
    'HI':'hainan',
    'NX':'ningxia',         
    'QH':'qinghai',
    'XZ':'xizang',         
    'HK':'hongkong'
    }
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    db = MySQLdb.connect("localhost", "root", "8571512411", "ics_scanning")
    cursor = db.cursor()
    for city in cities:
        #searchStr = raw_input("city:")
        url = 'http://ips.chacuo.net/view/s_'+ urllib.quote(city)
        req = urllib2.Request(url, headers = header)
        #fname = searchStr+'IP.txt'
        #f = codecs.open(fname,'w','utf-8')
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response, "html5lib")

        begin = []
        end = []

        begin = soup.find_all("span", class_="v_l")
        end = soup.find_all("span", class_="v_r")
        i = 0
        for sinIP in begin:
            ele = {}
            ele['begin'] = sinIP.string
            ele['end'] = end[i].string
            #result.append(ele)
            #add to mysql
            addTo_t_ip_subnet = "INSERT IGNORE INTO t_ip_subnet(city, ip_subnet_from, ip_subnet_to) VALUES('" + cities[city] + "','" + ele['begin'] + "','" + ele['end'] + "')"
            try:
                    cursor.execute(addTo_t_ip_subnet)
                    db.commit()
            except:
                    db.rollback()
            i = i+1
            
        #f.write(json.dumps(result, indent = 4))
    db.close()


if __name__ == "__main__":
    main()