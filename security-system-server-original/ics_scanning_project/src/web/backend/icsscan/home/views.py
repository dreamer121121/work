import logging

from django.core.paginator import Paginator
from django.db import connection

# Create your views here.
from django.db.models import Count

from common.utils import json_response
from home.models import Protocol, Website, Device

logger = logging.getLogger(__name__)

support_keys_for_host = ('ip', 'country', 'city', 'port', 'protocol')
support_keys_for_web = ('ip', 'port', 'city', 'port')
support_query_types = ('host', 'web', 'camera')

page_size = 10


def search(request):
    """
    API for searching
    :param request: 
    :return: 
    """
    result = ''
    if request.method == 'GET':
        query_condition = request.GET.get('q')
        query_type = request.GET.get('t')
        page_num = request.GET.get('p')

        logger.info(request.GET)

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

        search_params = {}

        query_list = query_condition.split(' ')
        for query in query_list:
            one_query = query.split(':')
            if len(one_query) != 2:
                continue

            search_params[one_query[0]] = one_query[1]

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
            continue

        if search_key == 'ip':
            search_key = 'ip_address'  # ip --> ip_address
        params[search_key + '__icontains'] = search_value

    all_webs = []
    if params:
        query = Website.objects.filter(**params)
        p = Paginator(query, page_size)
        total_num = p.count
        total_page = p.num_pages

        if page_num > total_num:
            page_num = total_num

        page_rows = p.page(page_num)
        if page_rows:
            all_webs = list(page_rows)
    else:
        total_num = 0
        total_page = 0

    return all_webs, total_page, page_num, total_num


def _get_devices(search_params, page_num):
    sql_select = 'SELECT a.ip_address, a.lat, a.lng, ' \
                 'a.asn, a.country, a.city,' \
                 'a.organization, a.ISP, a.dev_type,' \
                 'a.brand, a.status, a.add_time,' \
                 'a.update_time, a.access, b.port,' \
                 'b.protocol, b.banner, b.status as port_status '

    sql_from = 'FROM t_device a ' \
               'left join t_device_port b on a.ip_address = b.ip_address '

    if search_params:
        sql_where = 'WHERE '

        sql_params = []
        for search_key, search_value in search_params.items():
            if search_key not in support_keys_for_host:
                continue

            if search_key == 'ip':
                search_key = 'a.ip_address'  # ip --> ip_address
            sql_params.append(search_key + ' like "%%%s%%"' % search_value)

        sql_where += ' AND '.join(sql_params)
    else:
        sql_where = ''

    sql_count = 'select count(*) ' + sql_from + sql_where
    logger.info(sql_count)

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
    logger.info(sql)

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


def get_statistics_by_city(request):
    """
    statistics item numbers by city
    :param request: 
    :return: 
    """
    if request.method != 'GET':
        json_msg = {
            'error': 'Wrong HTTP method'
        }
        return json_response(json_msg)

    query_type = request.GET.get('t')
    if not query_type or query_type not in support_query_types:
        query_type = 'host'

    if query_type == 'host' or query_type == 'camera':
        rows = Device.objects.values('city').annotate(item_count=Count('ip_address'))
    else:
        rows = Website.objects.values('city').annotate(item_count=Count('ip_address'))

    total = 0
    for row in rows:
        total += row.get('item_count')

    if total > 0:
        for row in rows:
            row['percent'] = round(row.get('item_count') / total, 2)

    json_msg = {
        'result': list(rows)
    }

    return json_response(json_msg)
