# -*- coding:utf-8 -*-
import json

from django.core.paginator import Paginator
from django.db import connection
from django.http import HttpResponse, JsonResponse

from knowledgeBase.models import vulnerability, VulnerabilityDevice, vendor, instance, dev2vul, Protocol, Website
from knowledgeBase.models import InstancePort


def groupCount(request, type):
    list = []
    if type == "vulYear":
        list = vulnerability.objects.values_list('date')
    elif type == "devType":
        list = VulnerabilityDevice.objects.values_list('vendor')
    elif type == "venCountry":
        list = vendor.objects.values_list('country')
    elif type == "insCountry":
        list = instance.objects.values_list('country')
    elif type == "insProtocol":
        list = InstancePort.objects.values_list('protocol')
    elif type == "venDevice":
        list = VulnerabilityDevice.objects.values_list('vendor')

    temp = []
    for item in list:
        temp.append(item[0])

    if type == "vulYear":
        for i in range(len(temp)):
            temp[i] = temp[i][0:4]

    dic = {}
    for item in temp:
        if item == "":
            continue
        if item in dic:
            dic[item] += 1
        else:
            dic[item] = 1

    return HttpResponse(json.dumps(dic))


def getInstance(request):
    """
    设备探针菜单的地图显示设备使用此API
    :param request: 
    :return: 
    """
    cursor = connection.cursor()
    sql = 'SELECT a.ip, a.city, a.country, a.timestamp, a.lat, a.lon, b.port, b.protocol ' \
          'FROM knowledgeBase_instance a ' \
          'left join knowledgeBase_instanceport b on a.name = b.instance_id ' \
          'WHERE a.ip not like "%*%"'
    cursor.execute(sql)
    rowset = cursor.fetchall()

    devices = []
    for row in rowset:
        dev = dict()
        dev['ip'] = row[0]
        if row[1]:
            dev['city'] = row[1]
        else:
            dev['city'] = ''
        dev['country'] = row[2]
        dev['timestamp'] = row[3]
        dev['lat'] = row[4]
        dev['lon'] = row[5]
        dev['port'] = row[6]
        dev['ins_type'] = row[7]
        devices.append(dev)

    return HttpResponse(json.dumps(devices))


def getVulnerability(request):
    vulDeviceDic = {}
    for item in list(dev2vul.objects.values('device', 'vulnerability')):
        dev = item['device']
        vul = item['vulnerability']
        if vul in vulDeviceDic:
            vulDeviceDic[vul].append(dev)
        else:
            vulDeviceDic[vul] = [dev]

    result = list(vulnerability.objects.values())
    for vul in result:
        if vul['name'] in vulDeviceDic:
            vul['devices'] = vulDeviceDic[vul['name']]
        else:
            vul['devices'] = []

    return HttpResponse(json.dumps(result))


support_keys_for_host = ('ip', 'country', 'city', 'port', 'protocol', 'banner')
support_keys_for_web = ('ip', 'port', 'city', 'port', 'banner')
support_query_types = ('host', 'web', 'camera')
page_size = 10


def search(request):
    """
    API for searching devices
    :param request: 
    :return: 
    """
    if request.method == 'GET':
        print(request.GET)
        query_condition = request.GET.get('q')
        query_type = request.GET.get('t')
        page_num = request.GET.get('p')

        try:
            pn = int(page_num)
        except Exception:
            pn = 1

        if not query_type:
            query_type = 'host'

        if query_type not in support_query_types:
            query_type = 'host'

        if not query_condition:
            errmsg = {'error': 'Please enter a query condition!'}
            return json_response(errmsg)

        search_params = split_search_words(query_condition)
        print("search params: %s" % search_params)

        if query_type == 'host':
            result, total_page, curr_page, total_num = _get_devices(search_params, pn)

        elif query_type == 'web':
            result, total_page, curr_page, total_num = _get_website(search_params, pn)
        else:
            return json_response({'error': 'Invalid query type!'})

        json_msg = {
            'result': result,
            'tp': total_page,
            'p': curr_page,
            'tn': total_num
        }
    else:
        json_msg = {
            'error': 'Wrong HTTP method'
        }

    return json_response(json_msg)


def _get_website(search_params, page_num):
    if page_num <= 0:
        page_num = 1

    params = {}
    for search_key, search_value in search_params.items():
        if search_key not in support_keys_for_web:
            print("Error: not suport search key: %s" % search_key)
            continue

        params[search_key + '__icontains'] = search_value

    all_webs = []
    if params:
        query = Website.objects.filter(**params)
        p = Paginator(query, page_size)
        total_num = p.count
        total_page = p.num_pages
        print('total num: %s' % total_num)
        print('total page: %s' % total_page)

        if page_num > total_num:
            page_num = total_num

        if total_num > 0:
            page_rows = p.page(page_num)

            if page_rows:
                all_webs = list(page_rows)
    else:
        total_num = 0
        total_page = 0

    return all_webs, total_page, page_num, total_num


def _get_devices(search_params, page_num):
    sql_select = 'SELECT a.ip, a.lat, a.lon, ' \
                 'a.asn, a.country, a.city,' \
                 'a.organization, a.isp, a.os,' \
                 'a.vendor, a.service, a.timestamp,' \
                 'a.update_time, a.app, b.port,' \
                 'b.protocol, b.banner, b.status as port_status '

    sql_from = 'FROM knowledgeBase_instance a ' \
               'left join knowledgeBase_instanceport b on a.name = b.instance_id '

    # 过滤掉带星号的IP地址
    sql_where = 'WHERE a.ip not like "%*%" '

    if search_params:

        for search_key, search_value in search_params.items():
            if search_key not in support_keys_for_host:
                print("Not support the search key: %s" % search_key)
                continue

            if search_key == 'ip':
                search_key = 'a.ip'  # ip --> ip_address

            sql_where += ' AND ' + search_key + ' like "%%%s%%"' % search_value

    sql_count = 'select count(*) ' + sql_from + sql_where
    print(sql_count)

    cursor = connection.cursor()
    cursor.execute(sql_count)
    one_row = cursor.fetchone()
    if one_row:
        total_num = one_row[0]
    else:
        total_num = 0

    total_page, curr_page, from_idx = _get_page_params(page_num, total_num)
    sql_limit = ' limit %s, %s' % (from_idx, page_size)
    sql = sql_select + sql_from + sql_where + sql_limit

    print(sql)
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()

    all_devices = []
    for row in rows:
        device = {
            'ip': row[0],
            'lat': row[1],
            'lng': row[2],
            'asn': row[3],
            'country': row[4],
            'city': row[5],
            'organization': row[6],
            'ISP': row[7],
            'dev_type': row[8],
            'brand': row[9],
            'status': row[10],
            'add_time': row[11],
            'update_time': row[12],
            'access': row[13],
            'port': row[14],
            'protocol': row[15],
            'banner': row[16],
            'port_status': row[17],
        }
        all_devices.append(device)

    return all_devices, total_page, curr_page, total_num


def _get_page_params(page_num, total_num):
    """
    Pagination
    :param request: 
    :param total_num: 
    :return: 
    """
    if not page_num:
        curr_page = 1
    else:
        curr_page = int(page_num)
        if curr_page < 0:
            curr_page = 1

    total_page = int((total_num + page_size - 1) / page_size)

    if total_page < curr_page:
        curr_page = total_page

    if curr_page <= 0:
        curr_page = 1

    from_idx = (curr_page - 1) * page_size

    return total_page, curr_page, from_idx


def get_protocols(request):
    """
    API for get all protocols
    :param request: 
    :return: 
    """
    protocols = Protocol.objects.values()
    detail = {'protocols': list(protocols)}
    return json_response(detail)


def json_response(msg, ensure_ascii=False):
    """
    给django的JsonResponse增加中文编码支持
    :param ensure_ascii: 
    :param msg:
    :return:
    """
    dumps_params = {'ensure_ascii': ensure_ascii}
    return JsonResponse(msg, json_dumps_params=dumps_params)


def split_search_words(words):
    """
    切分输入的搜索内容，返回一个字典包括搜索key和value
    :param words:
    :return:
    """
    q = dict()

    words = words.lower()
    arr = words.split(':')
    if len(arr) == 1:
        q['banner'] = arr[0]
        return q

    segment = list()
    for item in arr:
        item = item.strip()
        if not item:
            continue

        if item.find(',') > 0:
            item_arr = item.split(',')
            segment.append(item_arr[0].strip())
            segment.append(item_arr[1].strip())
        elif item.find(' ') > 0:
            item_arr = item.split(' ')
            segment.append(item_arr[0].strip())
            segment.append(item_arr[1].strip())
        else:
            segment.append(item)

    for i in range(0, len(segment), 2):
        if (i + 2) > len(segment):
            break

        q[segment[i]] = segment[i + 1]

    return q