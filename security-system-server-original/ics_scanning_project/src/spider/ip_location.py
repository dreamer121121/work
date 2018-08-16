from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium.webdriver.support.ui as ui
import urllib
import re
import sys
import time
import mysql.connector
import os
import random

def Get_IP(ip):
    result = []
    print(ip)
    txtNode=raw_driver.find_element_by_id('ipaddress')
    ButtonNode=raw_driver.find_element_by_id('btnSearch')
    txtNode.clear()
    txtNode.send_keys(ip)
    ButtonNode.click()
    time.sleep(random.randint(2,3))
    name = raw_driver.find_element_by_xpath(u'//table[@id=\'ipTable\']')
    info =raw_driver.find_elements_by_xpath(u'//table[@id=\'ipTable\']/tbody/tr[2]/descendant::td')
    for node in info:
        result.append(node.text)
    print (result[2])
    print (result[3])
    return result
    
def deal(ip):
    a=0
    b=0
    num=[]
    ip_str=''
    for i in range(0,len(ip)):
        if ip[i]=='.':
            num[a]=int(ip_str)
            a=a+1
            b=0
        else:
            ip_str[b] = ip[i]
            b+=1
    num[a]=int(ip_str)
    return num
def gtr(ipt,ipf):
    for i in range(0,4):
        if(ipt[i]>ipf[i]):
            return True
        elif ipt[i]==ipf[i]:
            continue
        else:
            return False
    return False
def add_IP(ip):
    i=3
    while i>=0:
        ip[i]+=1
        if ip[i]>=256:
            ip[i]-=256
            i-=1
        else:
            break
def seperate(ip_from,ip_to):
    ipf=deal(ip_from)
    ipt=deal(ip_to)
    while gtr(ipt,ipf):
        Get_IP(str(ipf[0])+'.'+str(ipf[1])+'.'+str(ipf[2])+'.'+str(ipf[3]))
        ipf=add_IP(ipf)
def refresh(raw_driver):
    if raw_driver!="":
        raw_driver.quit()
        raw_driver = webdriver.PhantomJS()
    raw_driver.get("http://www.ipmarker.net")
    time.sleep(10)
    txtNode = raw_driver.find_element_by_id('ipaddress')
    ButtonNode = raw_driver.find_element_by_id('btnSearch')
    txtNode.send_keys("183.56.148.247")
    try:
        ButtonNode.click()
    except:
        refresh("")
    time.sleep(10)



dcap= DesiredCapabilities.PHANTOMJS.copy()
headers = {'Accept': '*/*',
'Host': 'localhuast:1337',

'Accept-Language': 'en-US,en;q=0.8',

'Cache-Control': 'max-age=0',

'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',

'Connection': 'keep-alive',
'Accept-Encoding':'gzip,deflate,sdch',

#'Referer':'http://www.baidu.com/'

}

for key, value in headers.items():
    dcap['phantomjs.page.customHeaders.{}'.format(key)] = value
#dcap = dict(DesiredCapabilities.PHANTOMJS)
#dcap["phantomjs.page.settings.userAgent"] = (
#    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
#)
raw_driver = webdriver.PhantomJS(desired_capabilities=dcap)
#PATH = 'C:/Users/H/AppData/Local/Google/Chrome/Application/chromedriver.exe'#the path of phantomjs
#os.environ["webdriver.chrome.driver"] = PATH
print (sys.argv)
url ="http://www.ipmarker.net/gis.jsp?ip=219.238.82.172&act=ip/"
url1="http://www.ipmarker.net/gis.jsp?ip="
url2="&act=ip/"
time.sleep(3)
try:
    refresh(raw_driver)
except:
    raw_driver.get(url)
cookie= raw_driver.get_cookies()
print cookie
#info =raw_driver.find_elements_by_xpath(u'//table[@id=\'ipTable\']/tbody/tr[2]/descendant::td')
#result1=[]
#for node in info:
#    result1.append(node.text)
#print (result1[2])
#print (result1[3])
conn=mysql.connector.connect(host='localhost',user='root',passwd='8571512411',db='ics_scan',use_unicode=True)
cur=conn.cursor()
if len(sys.argv)==1:
    print (1)
    cur.execute("select * from t_ip_subnet")
    results = cur.fetchall()
    for row in results:
        ip_from=row[2]
        ip_to=row[3]
        seperate(ip_from,ip_to)
elif sys.argv[1]=="--device":
    print (2)
    cur.execute("select ip from knowledgeBase_iplocation limit 14204,"+str(24874-14204))
    results = cur.fetchall()
    i = 0 
    for row in results:
        ip=row[0]
        #cur.execute("select * from t_device where ip ='"+ip+"'")
        count=0#len(cur.fetchall())
        if(count==0):
            try:
                print("try")
                result = Get_IP(ip)
            except:

                refresh(raw_driver)
                result = Get_IP(ip)
            #cur.execute("update knowledgeBase_iplocation set lat='"+result[3]+"',lng='"+result[2]+"',location='"+result[0]+"',timezone='"+result[1]+"',organization='"+result[4]+"',zip_code='"+result[5]+"',as_num='"+result[6]+"',as_name='"+result[7]+"',bgp_prefix='"+result[8]+"' where ip = '"+ip+"'")
            #conn.commit()
        else:
            continue
            #print(ip+"got")
            #cur.execute("select * from t_device where ip ='" + ip + "'")
            #result=cur.fetchone()
            #cur.execute("update knowledgeBase_iplocation set lat='" + result[3] + "',lng='" + result[4] + "',location='" + result[5] + "',timezone='" + result[6] + "',organization='" + result[9] + "',zip_code='" + result[
            #                 10] + "',as_num='" + result[11] + "',as_name='" + result[12] + "',bgp_prefix='" + result[
            #                 13] + "' where ip = '" + ip + "'")
else:
    print (3)
    raw_driver.get(url)
Get_IP("219.238.82.172")
raw_driver.quit()
