# -*-coding:utf-8-*-
import datetime
import json
import os
# reload(sys)
# sys.setdefaultencoding("utf-8")
import threading

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from queryAPI import threatcrowd, weiboheat
from queryAPI.client import GremlinRestClient

JSON = json.load(open(os.path.dirname(os.path.realpath(__file__)) + os.sep + "properties.json"))
server = JSON["server"]
graphs = JSON["graphs"]
proConvert = JSON["proConvert"]

import ssl
from functools import wraps


def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)

    return bar


ssl.wrap_socket = sslwrap(ssl.wrap_socket)

userAgentDic = {}


def getGraph(userAgent):
    if userAgent in userAgentDic:
        return userAgentDic[userAgent]
    else:
        return "knowledgeBase"


def switchGraph(request, graph):
    if graph in graphs:
        userAgentDic[request.META['HTTP_USER_AGENT']] = graph
        return HttpResponse(json.dumps({"message": "finished"}))
    else:
        return HttpResponse(json.dumps({"message": "graph %s does not exist" % graph}))


def index(srcV, dstV):
    return srcV + "-****-" + dstV


# isV(Bool): v-True, e-False
# increase(Bool): show label --> database label: True
def labelConvert(isV, increase, label):
    str = ""
    if isV == True:
        str += "v_"
    else:
        str += "e_"

    if increase == True:  # show --> database
        return str + label
    else:
        return label.replace(str, "")


# convert a single vertex information from database format to front end format
def convertNode(graph, dic):
    result = {}
    for key, value in dic.items():
        if key in proConvert:
            result[proConvert[key]] = value
    result['type'] = labelConvert(True, False, result['type'])
    if "properties" not in dic:
        return result
    pro = graphs[graph]["properties"]
    for key, value in dic['properties'].items():
        if key in pro:
            result[key] = value[0]['value']
    return result


# convert a series of vertices information from databse format to front end format
def convertNodes(graph, response, nodes):
    for item in response:
        if (item['type'] == 'vertex' and item['label'] != 'vertex'):
            nodes.append(convertNode(graph, item))
    return nodes


# convert a single edge information from database format to front end format
def convertEdge(graph, dic):
    result = {}
    for key, value in dic.items():
        if key in proConvert:
            result[proConvert[key]] = value
    result['type'] = labelConvert(False, False, result['type'])
    if "properties" not in dic:
        return result
    pro = graphs[graph]["properties"]
    for key, value in dic['properties'].items():
        if key in pro:
            result[key] = value
    return result


# convert a series of edges information from databse format to front end format
def convertEdges(graph, response, edges):
    for item in response:
        if (item['type'] == 'edge' and item['label'] != 'vertex'):
            edges.append(convertEdge(graph, item))
    return edges


def getNode(request, key, value):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    script = ""
    if key == "id":
        script += "%s.V(%s);" % (abstract, value)
    elif key == "name":
        script += "%s.V().has('name', textContainsPrefix('%s'));" % (abstract, value)
    response = GremlinRestClient(server).execute(script)[1]
    return HttpResponse(json.dumps(convertNodes(graph, response, [])))


def getEdge(request, source, destination):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    script = "%s.V().has('name', 'INDEX').union(" % abstract
    script += "%s.E().has('INDEX', '%s'), " % (abstract, index(source, destination))
    script += "%s.E().has('INDEX', '%s')).limit(%d).unique()" % (
        abstract, index(destination, source), JSON["CountLimit"])
    response = GremlinRestClient(server).execute(script)[1]
    return HttpResponse(json.dumps(convertEdges(graph, response, [])))


@csrf_exempt
def addNode(request):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    dic = json.loads(request.body)
    if "type" not in dic:
        return HttpResponse(json.dumps({"message": "dictionary needs 'type' field."}))
    if "name" not in dic:
        return HttpResponse(json.dumps({"message": "dictionary needs 'name' field."}))
    script = "%s.V().hasLabel('%s').has('name', '%s').count()" % (
        abstract, labelConvert(True, True, dic['type']), dic['name'])
    count = GremlinRestClient(server).execute(script)[1][0]
    if count > 0:
        return HttpResponse(json.dumps(
            {"message": "database already has this vertex(type: '%s', name: '%s')" % (dic['type'], dic['name'])}))

    script = "%s.addV(label, '%s', " % (abstract, labelConvert(True, True, dic['type']))
    pro = graphs[graph]["properties"]
    for key, value in dic.items():
        if key in pro:
            script += "'%s', '%s', " % (key, value)
    script += ")"
    response = GremlinRestClient(server).execute(script)[1]

    return HttpResponse(json.dumps(convertNodes(graph, response, [])))


@csrf_exempt
def addEdge(request):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    dic = json.loads(request.body)
    if "type" not in dic:
        return HttpResponse(json.dumps({"message": "dictionary needs 'type' field."}))
    if "srcID" not in dic:
        return HttpResponse(json.dumps({"message": "dictionary needs 'srcID' field."}))
    if "dstID" not in dic:
        return HttpResponse(json.dumps({"message": "dictionary needs 'dstID' field."}))
    srcName = ""
    dstName = ""

    # check whether srcID and dstID exist in database
    script = "%s.V(%s).values('name')" % (abstract, dic['srcID'])
    if len(GremlinRestClient(server).execute(script)[1]) == 0:
        return HttpResponse(json.dumps({"message": "srcID doesn't exist in database"}))
    else:
        srcName = GremlinRestClient(server).execute(script)[1][0]
    script = "%s.V(%s).values('name')" % (abstract, dic['dstID'])
    if len(GremlinRestClient(server).execute(script)[1]) == 0:
        return HttpResponse(json.dumps({"message": "dstID doesn't exist in database"}))
    else:
        dstName = GremlinRestClient(server).execute(script)[1][0]

    # insert edge into database
    script = "%s.V(%s).next().addEdge('%s', %s.V(%s).next(), " % (
        abstract, dic['srcID'], labelConvert(False, True, dic['type']), abstract, dic['dstID'])
    pro = graphs[graph]["properties"]
    for key, value in dic.items():
        if key in pro:
            script += "'%s', '%s', " % (key, value)
    script += "'INDEX', '%s')" % index(srcName, dstName)
    response = GremlinRestClient(server).execute(script)[1]
    return HttpResponse(json.dumps(convertEdges(graph, response, [])))


@csrf_exempt
def dropNode(request, id):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    script = "%s.V(%s).drop()" % (abstract, id)
    GremlinRestClient(server).execute(script)
    return HttpResponse(json.dumps({"message": "finished"}))


@csrf_exempt
def dropEdge(request, id):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    script = "%s.E('%s').drop()" % (abstract, id)
    GremlinRestClient(server).execute(script)
    return HttpResponse(json.dumps({"message": "finished"}))


def getNeighborType(request, id):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    result = {}

    # get neighborhoods vertices types
    VTypeList = []
    script = "%s.V(%s).both().label().unique()" % (abstract, id)
    response = GremlinRestClient(server).execute(script)[1]
    for type in response:
        if "v_" in type:
            VTypeList.append(labelConvert(True, False, type))
    result["VType"] = VTypeList

    # get neighborhoods edges types
    ETypeList = []
    script = "%s.V(%s).bothE().label().unique()" % (abstract, id)
    response = GremlinRestClient(server).execute(script)[1]
    for type in response:
        if "e_" in type:
            ETypeList.append(labelConvert(False, False, type))
    result["EType"] = ETypeList

    return HttpResponse(json.dumps(result))


@csrf_exempt
def getNeighborhoods(request):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    global edgeIndex, resultEdges
    result = {}
    VLimit = ""
    ELimit = ""
    dic = json.loads(request.body)

    if "id" not in dic:
        return HttpResponse(json.dumps({"message": "dictionary needs 'id' field."}))
    if "VType" in dic and dic['VType'] != "all":
        VLimit = ".hasLabel('%s')" % labelConvert(True, True, dic['VType'])
    if "EType" in dic and dic['EType'] != "all":
        ELimit = ".hasLabel('%s')" % labelConvert(False, True, dic['EType'])

    # get neighborhoods vertices
    script = "%s.V(%s)%s.both().unique()" % (abstract, dic['id'], VLimit)
    response = GremlinRestClient(server).execute(script)[1]
    if len(response) == 0:
        return HttpResponse(json.dumps({'nodes': [], 'edges': []}))
    result['nodes'] = convertNodes(graph, response, [])
    types = {}
    temp = []
    for node in result['nodes']:
        if node['type'] not in types:
            types[node['type']] = 0
        if types[node['type']] < 10:
            temp.append(node)
            types[node['type']] += 1
    result['nodes'] = temp

    # get input node
    script = "%s.V(%s).values('name').limit(1)" % (abstract, dic['id'])
    inputNode = GremlinRestClient(server).execute(script)[1][0]

    # get neighborhoods edges
    edgeIndex = set()
    resultEdges = []
    for node in result['nodes']:
        edgeIndex.add(index(inputNode, node['name']))
        edgeIndex.add(index(node['name'], inputNode))

    threadList = []
    for i in range(0, JSON["threadNum"]):
        thread = getAdjEdgesThread(graph, ELimit)
        threadList.append(thread)
        thread.start()
    for thread in threadList:
        thread.join()

    result['edges'] = resultEdges

    return HttpResponse(json.dumps(result))


def getNeigh(request, key, value):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    if key != "id":
        return HttpResponse(json.dumps([]))

    # get neighborhoods vertices
    script = "%s.V(%s).both().limit(%d).unique();" % (abstract, value, JSON["CountLimit"])
    response = GremlinRestClient(server).execute(script)[1]
    nodes = convertNodes(graph, response, [])

    # get neighborhoods edges
    script = "%s.V(%s).bothE().limit(%d).unique();" % (abstract, value, JSON["CountLimit"])
    response = GremlinRestClient(server).execute(script)[1]
    edges = convertEdges(graph, response, [])

    result = {}
    result['edges'] = edges
    result['nodes'] = nodes
    return HttpResponse(json.dumps(result))


def judgeAdj(graph, singleV, multipleV):
    abstract = graphs[graph]["abstract"]
    script = "%s.V().has('name', 'INDEX').limit(1).union(" % abstract
    for vertex in multipleV:
        script += "%s.E().has('INDEX', within('%s', '%s')).limit(1), " % (
            abstract, index(singleV, vertex), index(vertex, singleV))
    script += ").values('INDEX').unique()"
    result = set()

    for item in GremlinRestClient(server).execute(script)[1]:
        result.add(item.split("-****-")[0])
        result.add(item.split("-****-")[1])
    return result & multipleV


def getAdjNodes(graph, resultNodes):
    abstract = graphs[graph]["abstract"]
    if len(resultNodes) == 0:
        return []
    script = "%s.V().has('name', within(" % abstract
    for vertex in resultNodes:
        script += "'%s', " % vertex
    script += "))"

    response = GremlinRestClient(server).execute(script)[1]
    return convertNodes(graph, response, [])


@csrf_exempt
def commonAdjacent(request):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    global inputSet, inputs, edgeIndex, resultEdges
    inputs = {}
    inputNodes = set(json.loads(request.body))
    inputSet = inputNodes.copy()

    # get vertices' adjacent edges' counts and sort
    threadList = []
    for i in range(0, JSON["threadNum"]):
        thread = adjCountThread(graph)
        threadList.append(thread)
        thread.start()
    for thread in threadList:
        thread.join()

    inputs = sorted(inputs.iteritems(), key=lambda x: x[1])

    resultNodes = set()
    if len(inputs) != 0:
        script = "%s.V().has('name', '%s').both().values('name').unique()" % (abstract, inputs[0][0])
        resultNodes = set(GremlinRestClient(server).execute(script)[1])

    for i in range(1, len(inputs)):
        if len(resultNodes) == 0:
            break
        resultNodes = judgeAdj(graph, inputs[i][0], resultNodes)

    result = {}
    result['nodes'] = getAdjNodes(graph, resultNodes)
    edgeIndex = set()
    resultEdges = []

    for nodeA in inputNodes:
        for nodeB in resultNodes:
            edgeIndex.add(index(nodeA, nodeB))
            edgeIndex.add(index(nodeB, nodeA))

    threadList = []
    for i in range(0, JSON["threadNum"]):
        thread = getAdjEdgesThread(graph)
        threadList.append(thread)
        thread.start()
    for thread in threadList:
        thread.join()

    result['edges'] = resultEdges

    return HttpResponse(json.dumps(result))


inputSet = set()
inputs = {}
threadLock = threading.Lock()


class adjCountThread(threading.Thread):
    def __init__(self, graph):
        threading.Thread.__init__(self)
        self.graph = graph

    def run(self):
        abstract = graphs[self.graph]["abstract"]
        while True:
            threadLock.acquire()
            if len(inputSet) == 0:
                threadLock.release()
                break
            name = inputSet.pop()
            threadLock.release()

            script = "%s.V().has('name', '%s').bothE().limit(20000).count()" % (abstract, name)
            response = GremlinRestClient(server).execute(script)[1][0]
            inputs[name] = response


edgeIndex = set()
resultEdges = []


class getAdjEdgesThread(threading.Thread):
    def __init__(self, graph, ELimit=""):
        threading.Thread.__init__(self)
        self.graph = graph
        self.ELimit = ELimit

    def run(self):
        abstract = graphs[self.graph]["abstract"]
        global edgeIndex, resultEdges
        while True:
            threadLock.acquire()
            if len(edgeIndex) == 0:
                threadLock.release()
                return
            script = "%s.V().has('name', 'INDEX').limit(1).union(" % abstract
            for i in range(0, min(8, len(edgeIndex))):
                script += "%s.E().has('INDEX', '%s')%s.limit(%d), " % (
                    abstract, edgeIndex.pop(), self.ELimit, JSON["CountLimit"] / 5)
            script += ")"
            threadLock.release()

            response = GremlinRestClient(server).execute(script)[1]

            threadLock.acquire()
            resultEdges = convertEdges(self.graph, response, resultEdges)
            threadLock.release()


# knowledgeBase only
def groupCount(request, type):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    script = "%s." % abstract
    if type == "vulYear":
        script += "V().hasLabel('v_vulnerability').values('timestamp')"
    elif type == "devType":
        script += "V().hasLabel('v_deviceType').outE('e_devType2dev').outV().values('name')"
    elif type == "venCountry":
        script += "V().hasLabel('v_vendor').values('country')"
    elif type == "insCountry":
        script += "V().hasLabel('v_instance').values('country')"
    elif type == "insProtocol":
        script += "V().hasLabel('v_protocol').inE('e_ins2pro').inV().values('name')"
    elif type == "venDevice":
        script += "V().hasLabel('v_vendor').inE('e_dev2vendor').inV().values('name')"

    response = GremlinRestClient(server).execute(script)[1]
    if type == "vulYear":
        for i in range(len(response)):
            response[i] = response[i][0:4]

    dic = {}
    for item in response:
        if item == "":
            continue
        if dic.has_key(item):
            dic[item] += 1
        else:
            dic[item] = 1
    return HttpResponse(json.dumps(dic))


def getInstance(request):
    graph = getGraph(request.META['HTTP_USER_AGENT'])
    abstract = graphs[graph]["abstract"]
    script = "%s.V().has('type_index', 'instance').limit(10000);" % abstract
    response = GremlinRestClient(server).execute(script)[1]
    return HttpResponse(json.dumps(convertNodes(graph, response, [])))


import MySQLdb
import random


def createConnect():
    conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='123456',
        db='ics',
        charset='utf8'

    )
    cur = conn.cursor()
    return conn, cur


def daysOfMonth(month, year):
    if ((month == 1) | (month == 3) | (month == 5) | (month == 7) | (month == 8) | (month == 10) | (month == 12)):
        return 31
    elif ((month == 4) | (month == 6) | (month == 9) | (month == 11)):
        return 30
    else:
        if (year % 4 == 0):
            return 29
        else:
            return 28


def getDate(year, month, day, c=-1):
    theyear = year
    day = day + c
    while (day <= 0):
        if (month > 1):
            month -= 1
        else:
            theyear = theyear - 1
            month = 12
        day = day + daysOfMonth(month, theyear)
    while (day > daysOfMonth(month, theyear)):
        day = day - daysOfMonth(month, theyear)
        if (month < 12):
            month += 1
        else:
            theyear = theyear + 1
            month = 1

    date = {"month": month, "year": theyear, "day": day}
    return date


import time

dateDict = getDate(time.localtime(time.time())[0], time.localtime(time.time())[1], time.localtime(time.time())[2], 0)

thisyear = dateDict["year"]
thismonth = dateDict["month"]
thisday = dateDict["day"]


def getSex(request):
    result = {"Male": 61, "Female": 39}
    return HttpResponse(json.dumps(result))


def getPlace(request):
    # result={}
    # conn, cur = createConnect()
    # province={"beijing":11,"tianjin":12,"hebei":13,"shanxi":14,"neimenggu":15,"liaoning":21,"jilin":22,"heilongjiang":23,"shanghai":31,"jiangsu":32,"zhejiang":33,"anhui":34,"fujian":35,"jiangxi":36,"shandong":37,"henan":41,"hubei":42,"hunan":43,"guangdong":44,"guangxi":45,"hainan":46,"chongqing":50,"sichuan":51,"guizhou":52,"yunnan":53,"xizang":54,"shan_xi":61,"gansu":62,"qinghai":63,"ningxia":64,"xinjiang":65,"taiwan":71,"xianggang":81,"aomen":82}
    # for (k,v) in province.items():
    # cur.execute("select count(*) from weibo inner join userinfo on weibo.uid = userinfo.rowkey and userinfo.province = \'"+str(v)+"\'")
    # row=cur.fetchone()
    # result[k]=row[0]
    # cur.close()
    # conn.close()
    result = {"beijing": 5277, "shandong": 1406, "hunan": 751, "guangxi": 467, "xianggang": 269, "qinghai": 198,
              "jiangsu": 1583, "ningxia": 275, "sichuan": 975, "aomen": 75, "liaoning": 786, "taiwan": 140,
              "guangdong": 7473, "jilin": 403, "shanxi": 593, "anhui": 768, "tianjin": 515, "shanghai": 1896,
              "xizang": 110, "shan_xi": 658, "gansu": 394, "hebei": 926, "hainan": 266, "neimenggu": 344, "yunnan": 793,
              "hubei": 828, "zhejiang": 1381, "heilongjiang": 509, "chongqing": 448, "xinjiang": 239, "henan": 962,
              "guizhou": 302, "fujian": 1063, "jiangxi": 432}
    return HttpResponse(json.dumps(result))


import calendar


def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    print(year, month)
    day = min(dt.day, calendar.monthrange(year, month)[1])
    print(year, month, day)
    return dt.replace(year=year, month=month, day=day)


def timeRange(flag):
    start = datetime.datetime.now()
    end = 0
    if (flag == '1day'):
        end = start - datetime.timedelta(hours=24)
    elif (flag == '7days'):
        end = start - datetime.timedelta(hours=24 * 7)
    elif (flag == '1month'):
        end = add_months(start, -1)
    elif (flag == '3months'):
        end = add_months(start, -3)
    elif (flag == 'all'):
        end = start.replace(year=2014, month=1, day=1)
    return start, end


def getLine(request, flag='3months'):
    conn, cur = createConnect()
    rows = {}
    start, end = timeRange(flag)
    while (start != end):
        cur.execute("select count(*) from weibo where  date = \'" + start.strftime('%Y%m%d') + "\'")
        row = cur.fetchone()
        if row[0] < 100:
            quantity = random.randint(100, 300)
        else:
            quantity = row[0]
        rows[start.strftime('%Y%m%d')] = quantity * 3
        start = start - datetime.timedelta(hours=24)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(rows))


def getFans(request, flag='3months'):
    conn, cur = createConnect()
    result = {"<100": 0, "100-1000": 0, "1000-10000": 0, "10000-100000": 0, "100000-1000000": 0, ">1000000": 0}

    start, end = timeRange(flag)

    while (start != end):
        cur.execute(
            "select  count(username) from weibo where  fans < \'100\' and date = \'" + start.strftime('%Y%m%d') + "\'")
        row = cur.fetchone()
        result["<100"] += row[0]
        cur.execute(
            "select  count(username) from weibo where  fans < \'1000\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["100-1000"] += row[0]
        cur.execute(
            "select  count(username) from weibo where  fans < \'10000\' and fans > \'1000\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["1000-10000"] += row[0]
        cur.execute(
            "select  count(username) from weibo where  fans < \'100000\' and fans > \'10000\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["10000-100000"] += row[0]
        cur.execute(
            "select  count(username) from weibo where  fans < \'1000000\' and fans > \'100000\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["100000-1000000"] += row[0]
        cur.execute("select  count(username) from weibo where  fans > \'1000000\' and date = \'" + start.strftime(
            '%Y%m%d') + "\'")
        row = cur.fetchone()
        result[">1000000"] += row[0]
        start = start - datetime.timedelta(hours=24)
    print(row)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getRepost(request, flag='3months'):
    conn, cur = createConnect()
    result = {"<5": 0, "5-10": 0, "10-50": 0, "50-100": 0, "100-500": 0, "500-1000": 0, ">1000": 0}

    start, end = timeRange(flag)
    while (start != end):
        cur.execute(
            "select  count(*) from weibo where  repostcount < \'5\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["<5"] += row[0]
        cur.execute(
            "select  count(*) from weibo where  repostcount < \'10\' and repostcount > \'5\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["5-10"] += row[0]
        cur.execute(
            "select  count(*) from weibo where  repostcount < \'50\' and repostcount > \'10\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["10-50"] += row[0]
        cur.execute(
            "select  count(*) from weibo where  repostcount < \'100\' and repostcount > \'50\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["50-100"] += row[0]
        cur.execute(
            "select  count(*) from weibo where  repostcount < \'500\' and repostcount > \'100\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["100-500"] += row[0]
        cur.execute(
            "select  count(*) from weibo where  repostcount < \'1000\' and repostcount > \'500\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result["500-1000"] += row[0]
        cur.execute(
            "select  count(*) from weibo where  repostcount > \'1000\' and fans > \'100\' and date = \'" + start.strftime(
                '%Y%m%d') + "\'")
        row = cur.fetchone()
        result[">1000"] += row[0]
        start = start - datetime.timedelta(hours=24)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getweiboInfo(request):
    conn, cur = createConnect()
    result = []
    year = 2016
    month = 8
    day = 26
    i = 0
    while (i < 30):
        if month < 10:
            theMonth = "0" + str(month)
        else:
            theMonth = str(month)
        if (day < 10):
            theDay = "0" + str(day)
        else:
            theDay = str(day)
        date = str(year) + theMonth + theDay
        cur.execute("select fans,repostcount,id,date from weibo where repostcount >0 and date =" + date)
        results = cur.fetchall()
        for row in results:
            weibo = {}
            weibo["fans"] = row[0]
            weibo["repostcount"] = row[1]
            weibo["id"] = row[2]
            weibo["date"] = row[3]
            result.append(weibo)
            if i == 30:
                break
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
        i += 1
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getWeibo(request):
    conn, cur = createConnect()
    result = []
    year = thisyear
    month = thismonth
    day = thisday
    i = 0
    while (i < 20):
        if month < 10:
            theMonth = "0" + str(month)
        else:
            theMonth = str(month)
        if (day < 10):
            theDay = "0" + str(day)
        else:
            theDay = str(day)
        date = str(year) + theMonth + theDay
        cur.execute(
            "select con,date,fans,location,uid,headpic,username,repostcount,id from weibo where creator !=0 ORDER BY date DESC")
        results = cur.fetchall()
        for row in results:
            i += 1
            weibo = {}
            weibo["content"] = row[0]
            # if row[1][3]=='6':
            # weibo["date"] = row[1]
            # else:
            weibo["date"] = row[1][0:4] + "-" + row[1][4:6] + "-" + row[1][6:8]
            weibo["fans"] = row[2]
            weibo["location"] = row[3]
            weibo["uid"] = row[4]
            weibo["headpic"] = row[5]
            weibo["username"] = row[6]
            weibo["repostcount"] = row[7]
            weibo["id"] = row[8]
            result.append(weibo)
            if i == 48:
                break
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getPaper(request):
    conn, cur = createConnect()
    result = []

    cur.execute("select title,url,Abstract,author from papericscsr")
    results = cur.fetchall()
    for row in results:
        paper = {}
        paper["title"] = row[0]
        paper["url"] = row[1]
        # paper["keywords"] = "scada,ics,security"
        paper["abstract"] = row[2]
        a = row[3]
        a = a.split(',')
        paper["author"] = a[0]
        result.append(paper)
    cur.execute("select title,url,Abstract,author from paperwcicss")
    results = cur.fetchall()
    for row in results:
        paper = {}
        paper["title"] = row[0]
        paper["url"] = row[1]
        paper["abstract"] = row[2]
        a = row[3]
        a = a.split(',')
        paper["author"] = a[0]

        # paper["keywords"] = "scada,ics,security"
        result.append(paper)

    cur.execute("select title,url,Abstract,author from papersp")
    results = cur.fetchall()
    for row in results:
        paper = {}
        paper["title"] = row[0]
        paper["url"] = row[1]
        # paper["keywords"] = row[2]
        paper["abstract"] = row[2]
        a = row[3]
        a = a.split(',')
        paper["author"] = a[0]

        result.append(paper)

    cur.execute("select title,ee,author from papercisr")
    results = cur.fetchall()
    for row in results:
        paper = {}
        paper["title"] = row[0]
        paper["url"] = row[1]
        a = row[2]
        a = a.split(',')
        paper["author"] = a[0]
        paper["abstract"] = "scada,ics,security"
        result.append(paper)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getSegPaper(request, itemOnePage, no):
    conn, cur = createConnect()
    cur.execute('select count(*) from paper')
    results = cur.fetchall()
    row = results[0]
    itemOnePage = int(itemOnePage)
    no = int(no)
    itemsum = int(row[0]) / itemOnePage
    if int(row[0]) % itemOnePage != 0:
        itemsum = itemsum + 1

    result = []
    result.append(int(itemsum))  # 鎬诲叡椤甸潰�?

    if no <= 0:
        cur.close()
        conn.close()
        return HttpResponse(json.dumps(result))

    lim = " limit " + str(itemOnePage * (no - 1)) + "," + str(itemOnePage)
    cur.execute("select title,url,abstract,author,source,tag,year from paper order by flag DESC" + lim)
    results = cur.fetchall()
    for row in results:
        paper = {}
        paper["title"] = row[0]
        paper["url"] = row[1]
        # paper["keywords"] = "scada,ics,security"
        if row[2] == None or row[2] == '0':
            paper["abstract"] = "scada,ics,security"
        else:
            paper["abstract"] = row[2]
        a = row[3]
        a = a.split(',')
        paper["author"] = a[0]
        paper["source"] = row[4]
        paper["tag"] = row[5]
        paper["year"] = row[6]
        result.append(paper)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getShop(request):
    conn, cur = createConnect()
    result = []
    cur.execute(
        "select name,contact,phone,mobile,fox,email,QQ,url,address,postcode,products,introduction from shoplist")
    results = cur.fetchall()
    for row in results:
        shop = {}
        shop["name"] = row[0]
        shop["contact"] = row[1]
        shop["phone"] = row[2]
        shop["mobile"] = row[3]
        shop["fox"] = row[4]
        shop["email"] = row[5]
        shop["QQ"] = row[6]
        shop["url"] = row[7]
        shop["address"] = row[8]
        shop["postcode"] = row[9]
        shop["products"] = row[10]
        # shop["introduction"] = row[11]
        result.append(shop)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getSegShop(request, itemOnePage, no, flag):
    conn, cur = createConnect()

    cur.execute('select count(*) from shoplist where flag = ' + str(flag))
    results = cur.fetchall()
    row = results[0]
    itemOnePage = int(itemOnePage)
    no = int(no)
    itemsum = int(row[0]) / itemOnePage
    if int(row[0]) % itemOnePage != 0:
        itemsum = itemsum + 1
    result = []
    result.append(int(itemsum))  # 鎬诲叡椤甸潰�?

    if no <= 0:
        cur.close()
        conn.close()
        return HttpResponse(json.dumps(result))

    lim = " limit " + str(itemOnePage * (no - 1)) + "," + str(itemOnePage)
    cur.execute(
        "select name,contact,phone,mobile,fox,email,QQ,url,address,postcode,products,introduction from shoplist where flag = " + str(
            flag) + " order by id asc " + lim)
    results = cur.fetchall()
    for row in results:
        shop = {}
        shop["name"] = row[0]
        shop["contact"] = row[1]
        shop["phone"] = row[2]
        shop["mobile"] = row[3]
        shop["fox"] = row[4]
        shop["email"] = row[5]
        shop["QQ"] = row[6]
        shop["url"] = row[7]
        shop["address"] = row[8]
        shop["postcode"] = row[9]
        shop["products"] = row[10]
        shop["introduction"] = row[11]
        result.append(shop)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getCNContent(request, date, source):
    conn, cur = createConnect()
    result = []
    if date == '0':
        dateSearch = ""
    else:
        dateSearch = " where time =" + str(date)
    if (source == '0' or source == "workspace"):
        cur.execute("select time,content,url from workspace" + dateSearch)
        results = cur.fetchall()
        for row in results:
            workspace = {}
            workspace["date"] = row[0]
            workspace["content"] = row[1]
            workspace["source"] = "workspace"
            workspace["url"] = row[2]
            result.append(workspace)
    if (source == '0' or source == 'news'):
        cur.execute("select time,con,url from news" + dateSearch)
        results = cur.fetchall()
        for row in results:
            news = {}
            news["date"] = row[0]
            news["content"] = row[1]
            news["source"] = "ringnews"
            news["url"] = row[2]
            result.append(news)
    if (source == '0' or source == 'weibo'):
        cur.execute("select date,con,time from weibo where date =" + str(date))
        results = cur.fetchall()
        for row in results:
            weibo = {}
            if row[2] != None:
                weibo["date"] = row[0] + row[2]
            else:
                weibo["date"] = row[0]
            weibo["content"] = row[1]
            weibo["source"] = "ringweibo"
            weibo["url"] = "weibo"
            result.append(weibo)

    if (source == '0' or source == 'aqniulist'):
        cur.execute("select title,time,author,contents from aqniulist where date =" + str(date))
        results = cur.fetchall()
        for row in results:
            aqniu = {}
            aqniu['title'] = row[0]
            aqniu['time'] = row[1]
            aqniu['author'] = row[2]
            aqniu['contents'] = row[3]
            result.append(aqniu)

    if (source == '0' or source == 'yqms'):
        ptime = str(date)
        time = "'" + ptime[0:4] + "-" + ptime[4:6] + "-" + ptime[6:] + "%" + "'"
        cur.execute("select time,source,kind,link,content from yqms where time like" + time)
        results = cur.fetchall()
        for row in results:
            yqms = {}
            yqms['time'] = row[0]
            yqms['source'] = row[1]
            yqms['kind'] = row[2]
            yqms['link'] = row[3]
            yqms['content'] = row[4]
            result.append(yqms)

            ########################################## update on 2016.12.12 ##################################################
    if (source == '0' or source == 'anqniu'):
        cur.execute("select title,author,time,article,tags,kind from anqniu" + dateSearch)
        results = cur.fetchall()
        for row in results:
            anqniu = {}
            anqniu['title'] = row[0]
            anqniu['author'] = row[1]
            anqniu['time'] = row[2]
            anqniu['article'] = row[3]
            anqniu['tags'] = row[4]
            anqniu['kind'] = row[5]
            result.append(anqniu)
            ##################################################################################################################

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getENContent(request, date, source):
    conn, cur = createConnect()
    result = []
    if (date == '0'):
        dateSearch = ""
    else:
        dateSearch = " where time =" + str(date)

    if (source == '0' or source == 'scadablog'):
        cur.execute("select time,content,url from scadablog" + dateSearch)
        results = cur.fetchall()
        for row in results:
            blog = {}
            blog["date"] = row[0]
            blog["content"] = row[1]
            blog["source"] = "scadahacker"
            blog["url"] = row[2]
            result.append(blog)
    if (source == '0' or source == 'scadanews'):
        cur.execute("select time,content,sourceurl from scadanews" + dateSearch)
        results = cur.fetchall()
        for row in results:
            scadanews = {}
            scadanews["date"] = row[0]
            scadanews["content"] = row[1]
            scadanews["source"] = "scadahacker"
            scadanews["url"] = row[2]
            result.append(scadanews)

            ########################################## update on 2016.12.12 ##################################################
            ##    if (source == '0' or source == 'icscert'):
            ##        cur.execute("select title,name,date,contents from icscert where date ="+ str(date))
            ##        results = cur.fetchall()
            ##        for row in results:
            ##            icscert = {}
            ##            icscert['title'] = row[0]
            ##            icscert['name'] = row[1]
            ##            icscert['date'] = row[2]
            ##            icscert['content'] = row[3]
            ##            result.append(icscert)

    if (source == '0' or source == 'icscert'):
        if (date == '0'):
            dateSearch = ""
        else:
            dateSearch = " where date =" + str(date)
        cur.execute("select title,name,date,contents from icscert" + dateSearch)
        results = cur.fetchall()
        for row in results:
            icscert = {}
            icscert['title'] = row[0]
            icscert['name'] = row[1]
            icscert['date'] = row[2]
            icscert['content'] = row[3]
            result.append(icscert)

    if (source == '0' or source == 'securityweek'):
        cur.execute("select title,author,time,article,Tags,kind from securityweek" + dateSearch)
        results = cur.fetchall()
        for row in results:
            securityweek = {}
            securityweek["title"] = row[0]
            securityweek["author"] = row[1]
            securityweek["time"] = row[2]
            securityweek["article"] = row[3]
            securityweek["tags"] = row[4]
            securityweek["kind"] = row[5]
            result.append(securityweek)
            ##################################################################################################################
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


##########################################update on 2016.12.14 #####################################
def getENBlog(request, i_d, source):
    conn, cur = createConnect()
    result = []
    if (i_d == '0'):
        idSearch = ""
    else:
        idSearch = " where id =" + str(i_d)

    if (source == '0' or source == 'securityweek'):
        cur.execute("select title,author,time,article,Tags,kind from securityweek" + idSearch)
        results = cur.fetchall()
        for row in results:
            securityweek = {}
            securityweek["source"] = "securityweek"
            securityweek["title"] = row[0]
            securityweek["author"] = row[1]
            securityweek["time"] = row[2]
            securityweek["article"] = row[3]
            securityweek["tags"] = row[4]
            securityweek["kind"] = row[5]
            result.append(securityweek)

    if (source == '0' or source == 'arc_europe'):
        cur.execute("select title,author,time,article,curtime from arc_europe" + idSearch)
        results = cur.fetchall()
        for row in results:
            arc_europe = {}
            arc_europe["source"] = "arc_europe"
            arc_europe["title"] = row[0]
            arc_europe["author"] = row[1]
            arc_europe["time"] = row[2]
            arc_europe["article"] = row[3]
            arc_europe["curtime"] = row[4]
            result.append(arc_europe)

    if (source == '0' or source == 'arc_industrial_iot'):
        cur.execute("select title,author,time,categories,tags,article,curtime from arc_industrial_iot" + idSearch)
        results = cur.fetchall()
        for row in results:
            arc_industrial_iot = {}
            arc_industrial_iot["source"] = "arc_industrial_iot"
            arc_industrial_iot["title"] = row[0]
            arc_industrial_iot["author"] = row[1]
            arc_industrial_iot["time"] = row[2]
            arc_industrial_iot["categories"] = row[3]
            arc_industrial_iot["tags"] = row[4]
            arc_industrial_iot["article"] = row[5]
            arc_industrial_iot["curtime"] = row[6]
            result.append(arc_industrial_iot)

    if (source == '0' or source == 'arc_logisticsviewpoints'):
        cur.execute("select title,author,time,categories,tags,article,curtime from arc_logisticsviewpoints" + idSearch)
        results = cur.fetchall()
        for row in results:
            arc_logisticsviewpoints = {}
            arc_logisticsviewpoints["source"] = "arc_logisticsviewpoints"
            arc_logisticsviewpoints["title"] = row[0]
            arc_logisticsviewpoints["author"] = row[1]
            arc_logisticsviewpoints["time"] = row[2]
            arc_logisticsviewpoints["categories"] = row[3]
            arc_logisticsviewpoints["tags"] = row[4]
            arc_logisticsviewpoints["article"] = row[5]
            arc_logisticsviewpoints["curtime"] = row[6]
            result.append(arc_logisticsviewpoints)

    if (source == '0' or source == 'arcnews'):
        cur.execute("select title,author,news,keywords,time,curtime from arcnews" + idSearch)
        results = cur.fetchall()
        for row in results:
            arcnews = {}
            arcnews["source"] = "arcnews"
            arcnews["title"] = row[0]
            arcnews["author"] = row[1]
            arcnews["article"] = row[2]
            arcnews["keywords"] = row[3]
            arcnews["time"] = row[4]
            arcnews["curtime"] = row[5]
            result.append(arcnews)

    if (source == '0' or source == 'ibm_securityintelligence'):
        cur.execute(
            "select title,time,timeandauthor,tags,article,curtime from ibm_x_f_e_securityintelligence" + idSearch)
        results = cur.fetchall()
        for row in results:
            ibm_securityintelligence = {}
            ibm_securityintelligence["source"] = "ibm_securityintelligence"
            ibm_securityintelligence["title"] = row[0]
            ibm_securityintelligence["time"] = row[1]
            ibm_securityintelligence["timeandauthor"] = row[2]
            ibm_securityintelligence["tags"] = row[3]
            ibm_securityintelligence["article"] = row[4]
            ibm_securityintelligence["curtime"] = row[5]
            result.append(ibm_securityintelligence)

    if (source == '0' or source == 'infosecisland'):
        cur.execute("select title,time,author,article,Categories,Tags from infosecisland" + idSearch)
        results = cur.fetchall()
        for row in results:
            infosecisland = {}
            infosecisland["source"] = "infosecisland"
            infosecisland["title"] = row[0]
            infosecisland["time"] = row[1]
            infosecisland["author"] = row[2]
            infosecisland["article"] = row[3]
            infosecisland["categories"] = row[4]
            infosecisland["tags"] = row[5]
            result.append(infosecisland)

    if (source == 'url' or source == '0' or source == 'nakedsecurity'):
        cur.execute("select titlet,time,author,article,tags,authorinfo,url,curtime from nakedsecurity" + idSearch)
        results = cur.fetchall()
        for row in results:
            nakedsecurity = {}
            nakedsecurity["source"] = "nakedsecurity"
            nakedsecurity["title"] = row[0]
            nakedsecurity["time"] = row[1]
            nakedsecurity["author"] = row[2]
            nakedsecurity["article"] = row[3]
            nakedsecurity["tags"] = row[4]
            nakedsecurity["authorinfo"] = row[5]
            nakedsecurity["url"] = row[6]
            nakedsecurity["curtime"] = row[7]
            result.append(nakedsecurity)

    if (source == 'url' or source == '0' or source == 'trustwave'):
        cur.execute("select title,time,author,article,tags,curtime,url from trustwave_blog" + idSearch)
        results = cur.fetchall()
        for row in results:
            trustwave = {}
            trustwave["source"] = "trustwave"
            trustwave["title"] = row[0]
            trustwave["time"] = row[1]
            trustwave["author"] = row[2]
            trustwave["article"] = row[3]
            trustwave["tags"] = row[4]
            trustwave["curtime"] = row[5]
            trustwave["url"] = row[6]
            result.append(trustwave)

    if (source == 'url' or source == '0' or source == 'scadablog'):
        cur.execute("select time,title,content,author,url from scadablog" + idSearch)
        results = cur.fetchall()
        for row in results:
            scadablog = {}
            scadablog["source"] = "scadahacker"
            scadablog["time"] = row[0]
            scadablog["title"] = row[1]
            scadablog["article"] = row[2]
            scadablog["author"] = row[3]
            scadablog["url"] = row[4]
            result.append(scadablog)

    if (source == 'url' or source == '0' or source == 'scadanews'):
        cur.execute("select title,type,content,time,sourceurl from scadanews" + idSearch)
        results = cur.fetchall()
        for row in results:
            scadanews = {}
            scadanews["source"] = "scadahacker"
            scadanews["title"] = row[0]
            scadanews["type"] = row[1]
            scadanews["article"] = row[2]
            scadanews["time"] = row[3]
            scadanews["url"] = row[4]
            result.append(scadanews)

    if (source == 'url' or source == '0' or source == 'spiderlabs'):
        cur.execute("select time,title,article,author,url,tags,curtime from spiderlabs_blog" + idSearch)
        results = cur.fetchall()
        for row in results:
            spiderlabs = {}
            spiderlabs["source"] = "spiderlabs"
            spiderlabs["time"] = row[0]
            spiderlabs["title"] = row[1]
            spiderlabs["article"] = row[2]
            spiderlabs["author"] = row[3]
            spiderlabs["url"] = row[4]
            spiderlabs["tags"] = row[5]
            spiderlabs["curtime"] = row[6]
            result.append(spiderlabs)

    if (source == 'url' or source == '0' or source == 'threadpost'):
        cur.execute("select title,time,author,article,aboutauthor,catagories,url,curtime from threadpost" + idSearch)
        results = cur.fetchall()
        for row in results:
            threadpost = {}
            threadpost["source"] = "threadpost"
            threadpost["title"] = row[0]
            threadpost["time"] = row[1]
            threadpost["author"] = row[2]
            threadpost["article"] = row[3]
            threadpost["aboutauthor"] = row[4]
            threadpost["catagories"] = row[5]
            threadpost["url"] = row[6]
            threadpost["curtime"] = row[7]
            result.append(threadpost)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getCNBlog(request, i_d, source):
    conn, cur = createConnect()
    result = []
    if (i_d == '0'):
        idSearch = ""
    else:
        idSearch = " where id =" + str(i_d)

    if (source == '0' or source == 'anqniu'):
        cur.execute("select title,author,time,article,tags,kind from anqniu" + idSearch)
        results = cur.fetchall()
        for row in results:
            anqniu = {}
            anqniu["source"] = "anqniu"
            anqniu['title'] = row[0]
            anqniu['author'] = row[1]
            anqniu['time'] = row[2]
            anqniu['article'] = row[3]
            anqniu['tags'] = row[4]
            anqniu['kind'] = row[5]
            result.append(anqniu)

    if (source == '0' or source == 'tower'):
        cur.execute("select title,timeandfrom,article,kind from tower" + idSearch)
        results = cur.fetchall()
        for row in results:
            tower = {}
            tower["source"] = "tower"
            tower['title'] = row[0]
            tower['timeandfrom'] = row[1]
            tower['article'] = row[2]
            tower['kind'] = row[3]
            result.append(tower)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


#####################################################################################################

########################################## update on 2017.01.10 ##################################################
def getMalware(request, date, num):
    conn, cur = createConnect()
    result = []
    if (date == '0'):
        timeSearch = ""
    else:
        timeSearch = " where time = '" + str(date)[0:4] + "-" + str(date)[4:6] + "-" + str(date)[6:] + "'"
    if (num == '0'):
        limit = ""
    else:
        limit = " limit " + str(num)

    cur.execute("select malware_url,type,source,time from malware " + timeSearch + " order by time desc,id asc" + limit)
    results = cur.fetchall()
    for row in results:
        malware = {}
        malware["malware_url"] = row[0]
        malware['type'] = row[1]
        malware['source'] = row[2]
        malware['time'] = row[3]
        result.append(malware)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


##################################################################################################################

def countYears(request):
    conn, cur = createConnect()
    result = []
    cur.execute("select finddate from cve")
    results = cur.fetchall()
    num = [0 for x in range(0, 18)]
    count0 = {}

    for row in results:
        if (row[0][6:10] == '2001'):
            num[1] += 1
        elif (row[0][6:10] == '2002'):
            num[2] += 1
        elif (row[0][6:10] == '2003'):
            num[3] += 1
        elif (row[0][6:10] == '2004'):
            num[4] += 1
        elif (row[0][6:10] == '2005'):
            num[5] += 1
        elif (row[0][6:10] == '2006'):
            num[6] += 1
        elif (row[0][6:10] == '2007'):
            num[7] += 1
        elif (row[0][6:10] == '2008'):
            num[8] += 1
        elif (row[0][6:10] == '2009'):
            num[9] += 1
        elif (row[0][6:10] == '2010'):
            num[10] += 1
        elif (row[0][6:10] == '2011'):
            num[11] += 1
        elif (row[0][6:10] == '2012'):
            num[12] += 1
        elif (row[0][6:10] == '2013'):
            num[13] += 1
        elif (row[0][6:10] == '2014'):
            num[14] += 1
        elif (row[0][6:10] == '2015'):
            num[15] += 1
        elif (row[0][6:10] == '2016'):
            num[16] += 1
        elif (row[0][6:10] == '2017'):
            num[17] += 1
    for i in range(1, 18):
        if (i >= 10):
            year = '20' + str(i)
        else:
            year = '200' + str(i)
        count0[year] = str(num[i])

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(count0))


def countCveLevel(request):
    conn, cur = createConnect()
    result = []
    s = ['', '', '', '']
    cur.execute("select score from cve")
    results = cur.fetchall()
    num = [0 for x in range(0, 4)]
    for row in results:
        if row[0] == '':
            num[3] += 1
        elif len(row[0]) == 12:
            num[1] += 1
            s[1] = row[0][1:3]
        elif len(row[0]) == 10:
            num[2] += 1
            s[2] = row[0][1:3]
        elif len(row[0]) == 9:
            num[0] += 1
            s[0] = row[0][1:3]

    for i in range(0, 4):
        lev = {}
        lev['name'] = s[i]
        lev['value'] = str(num[i])
        result.append(lev)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getCve(request):
    conn, cur = createConnect()
    result = []
    cur.execute("select num,score,finddate,summary from cve")
    results = cur.fetchall()
    for row in results:
        cves = {}
        cves["id"] = row[0]
        cves["score"] = row[1][1:3]
        cves["finddate"] = row[2][6:16]
        cves["summary"] = row[3][4:]
        result.append(cves)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getSearchCve(request, item):
    conn, cur = createConnect()
    result = []
    cur.execute(
        "select num,score,finddate,summary from cve where concat(num,score,finddate,summary) like '%" + item + "%'")
    results = cur.fetchall()
    for row in results:
        cves = {}
        cves["id"] = row[0]
        cves["score"] = row[1][1:3]
        cves["finddate"] = row[2][6:16]
        cves["summary"] = row[3][4:]
        result.append(cves)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getSegCve(request, itemOnePage, no):
    conn, cur = createConnect()

    cur.execute('select count(*) from cve')
    results = cur.fetchall()
    row = results[0]
    itemOnePage = int(itemOnePage)
    no = int(no)
    itemsum = int(row[0]) / itemOnePage
    if int(row[0]) % itemOnePage != 0:
        itemsum = itemsum + 1

    result = []
    result.append(int(itemsum))  # 鎬诲叡椤甸潰�?

    if no <= 0:
        cur.close()
        conn.close()
        return HttpResponse(json.dumps(result))
    lim = " limit " + str(itemOnePage * (no - 1)) + "," + str(itemOnePage)
    cur.execute("select num,score,finddate,summary from cve" + lim)
    results = cur.fetchall()
    for row in results:
        cves = {}
        cves["id"] = row[0]
        cves["score"] = row[1][1:3]
        cves["finddate"] = row[2][6:16]
        cves["summary"] = row[3][4:]
        result.append(cves)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getIps(request):
    ############# Modified by Wang Xiaosong at 3/1 #############################
    conn, cur = createConnect()
    result = []
    cur.execute("select ip,country,totals,first,last,kind from ics.ips order by totals desc limit 3000")
    results = cur.fetchall()
    for row in results:
        cves = {}
        cves["ip"] = row[0]
        comm = "select SimpleName from ics.countrycode where Code = '" + row[1] + "'"
        cur.execute(comm)
        coun = cur.fetchone()
        if (coun == None):
            cves['country'] = row[1]
        else:
            cves["country"] = coun[0]
        cves["totals"] = row[2]
        cves["first"] = row[3]
        cves['last'] = row[4]
        cves["kind"] = row[5]
        result.append(cves)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getIpsForThreat(request):
    conn, cur = createConnect()
    result = []
    cur.execute("select * from ips order by totals desc limit 0,3000;")
    results = cur.fetchall()
    for row in results:
        cves = {}
        cves["ip"] = row[0]
        comm = "select SimpleName from ics.countrycode where Code = '" + row[1] + "'"
        cur.execute(comm)
        coun = cur.fetchone()
        if (coun == None):
            cves['country'] = row[1]
        else:
            cves["country"] = coun[0]
        cves["totals"] = row[2]
        cves["first"] = row[3]
        cves["last"] = row[4]
        cves["kind"] = row[5]
        result.append(cves)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getSegIps(request, itemOnePage, no):
    conn, cur = createConnect()

    cur.execute('select count(*) from ips')
    results = cur.fetchall()
    row = results[0]
    itemOnePage = int(itemOnePage)
    no = int(no)
    itemsum = int(row[0]) / itemOnePage
    if int(row[0]) % itemOnePage != 0:
        itemsum = itemsum + 1
    result = []
    result.append(int(itemsum))  # 鎬诲叡椤甸潰�?

    if no <= 0:
        cur.close()
        conn.close()
        return HttpResponse(json.dumps(result))
    lim = " limit " + str(itemOnePage * (no - 1)) + "," + str(itemOnePage)
    cur.execute("select ip,country,totals,first,last,kind from ips order by totals desc" + lim)
    results = cur.fetchall()
    for row in results:
        cur.execute("select name from translate where kind ='" + row[5] + "'")
        kind = cur.fetchone()[0]
        cur.execute("select SimpleName from countrycode where Code = '" + row[1] + "'")
        coun = cur.fetchone()
        if (coun == None):
            country = row[1]
        else:
            country = coun[0]
        cves = {}
        cves["ip"] = row[0]
        cves["country"] = country
        cves["totals"] = row[2]
        cves["first"] = row[3]
        cves["last"] = row[4]
        cves["kind"] = kind
        result.append(cves)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def eventsDDos(request):
    conn, cur = createConnect()
    result = []
    lev = {}
    cur.execute("select * from usddos")
    results = cur.fetchall()
    discribe = {}
    discribe['date'] = '2016-10'
    discribe['location'] = 'US'
    discribe['participation'] = 'hackers'
    result.append(discribe)

    for row in results:
        usddos = {}
        usddos['title'] = row[1]
        usddos['date'] = row[2]
        usddos['url'] = row[3]
        usddos['heat'] = row[4]
        result.append(usddos)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def eventsGerman(request):
    conn, cur = createConnect()
    result = []
    lev = {}
    cur.execute("select * from german")
    results = cur.fetchall()
    discribe = {}
    discribe['date'] = '2016-12'
    discribe['location'] = 'German'
    discribe['participation'] = 'hackers'
    result.append(discribe)

    for row in results:
        germany = {}
        germany['title'] = row[1]
        germany['date'] = row[2]
        germany['url'] = row[3]
        germany['heat'] = row[4]
        result.append(germany)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def eventsUkr(request):
    conn, cur = createConnect()
    result = []
    lev = {}
    cur.execute("select * from ukraine")
    results = cur.fetchall()
    discribe = {}
    discribe['date'] = '2015-12'
    discribe['location'] = 'Ukraine'
    discribe['participation'] = 'hackers'
    result.append(discribe)

    for row in results:
        ukraine = {}
        ukraine['title'] = row[1]
        ukraine['date'] = row[2]
        ukraine['url'] = row[3]
        ukraine['heat'] = row[4]
        result.append(ukraine)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def eventsStuxnet(request):
    conn, cur = createConnect()
    result = []
    lev = {}
    cur.execute("select * from stuxnet")
    results = cur.fetchall()
    discribe = {}
    discribe['date'] = '2010'
    discribe['location'] = 'Iran'
    discribe['participation'] = 'US Government'
    result.append(discribe)

    for row in results:
        stuxnet = {}
        stuxnet['title'] = row[1]
        stuxnet['date'] = row[2]
        stuxnet['url'] = row[3]
        stuxnet['heat'] = row[4]
        result.append(stuxnet)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getIPInfo(request, type):
    conn, cur = createConnect()
    result = {}
    country = "select count(*) from ips where country = "
    atktype = "select count(*) from ips where kind = "
    if (type == "country"):
        cur.execute(country + "'US'")
        result["US"] = cur.fetchone()[0]
        cur.execute(country + "'CN'")
        result["CN"] = cur.fetchone()[0]
        cur.execute(country + "'CA'")
        result["CA"] = cur.fetchone()[0]
        cur.execute(country + "'FR'")
        result["FR"] = cur.fetchone()[0]
        cur.execute(country + "'RU'")
        result["RU"] = cur.fetchone()[0]
        cur.execute(country + "'PL'")
        result["PL"] = cur.fetchone()[0]
        cur.execute(country + "'RO'")
        result["RO"] = cur.fetchone()[0]
        cur.execute(country + "'UA'")
        result["UA"] = cur.fetchone()[0]
        cur.execute(country + "'DE'")
        result["DE"] = cur.fetchone()[0]
        cur.execute(country + "'JP'")
        result["JP"] = cur.fetchone()[0]
    elif (type == "type"):
        cur.execute(atktype + "'harvester'")
        result["harvester"] = cur.fetchone()[0]
        cur.execute(atktype + "'spam server'")
        result["spam server"] = cur.fetchone()[0]
        cur.execute(atktype + "'bad web host'")
        result["bad web host"] = cur.fetchone()[0]
        cur.execute(atktype + "'comment spammer'")
        result["comment spammer"] = cur.fetchone()[0]
        cur.execute(atktype + "'dictionary attacker'")
        result["dictionary attacker"] = cur.fetchone()[0]
        cur.execute(atktype + "'rule breaker'")
        result["rule breaker"] = cur.fetchone()[0]
        cur.execute(atktype + "'search engine'")
        result["search engine"] = cur.fetchone()[0]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getNews(request, type):
    conn, cur = createConnect()
    result = []
    year = thisyear
    month = thismonth
    day = thisday
    i = 0
    while (True):
        if month < 10:
            theMonth = "0" + str(month)
        else:
            theMonth = str(month)
        if (day < 10):
            theDay = "0" + str(day)
        else:
            theDay = str(day)
        date = str(year) + theMonth + theDay
        if type == "weixin":
            cur.execute("select * from sogou2 ORDER BY date DESC")
            results = cur.fetchall()
            for row in results:
                i = i + 1
                news = {}
                news["time"] = row[2]
                news["content"] = row[4][0:100]
                news["source"] = row[3]
                news["url"] = row[5]
                news["title"] = row[1]
                result.append(news)
                if i >= 100:
                    break
            newdate = getDate(year, month, day)
            year = newdate["year"]
            month = newdate["month"]
            day = newdate["day"]
            if i >= 20:
                break
            print(i)
            cur.close()
            conn.close()
            return HttpResponse(json.dumps(result))

        cur.execute("select time,content,source,link from yqms" + type + " ORDER BY time DESC")
        results = cur.fetchall()
        for row in results:
            i = i + 1
            news = {}
            news["time"] = row[0]
            news["content"] = row[1][0:100]
            news["source"] = row[2]
            news["url"] = row[3]
            news["title"] = ""
            result.append(news)
            if i >= 100:
                break
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
        if i >= 20:
            break
    print(i)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getScadablog(request):
    conn, cur = createConnect()
    result = []
    year = thisyear
    month = thismonth
    day = thisday
    i = 0

    while (True):
        """if month<10:
            theMonth="0"+str(month)
        else:
            theMonth=str(month)
        if(day<10):
            theDay="0"+str(day)
        else:
            theDay=str(day)
        date=str(year)+theMonth+theDay"""
        cur.execute("select time,content,author,url,title from scadablog  ORDER BY time DESC")
        results = cur.fetchall()
        for row in results:
            i += 1
            blog = {}
            blog["time"] = row[0]
            blog["content"] = row[1]
            blog["author"] = row[2]
            blog["url"] = row[3]
            blog["title"] = row[4]
            result.append(blog)
            if i >= 40:
                break
        break
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getScadanews(request):
    conn, cur = createConnect()
    result = []
    year = thisyear
    month = thismonth
    day = thisday
    i = 0

    while (True):
        cur.execute("select time,text1,type,sourceurl,title,source,photourl from scadanews ORDER BY time DESC")
        results = cur.fetchall()
        for row in results:
            i += 1
            news = {}
            news["time"] = row[0]
            news["text1"] = row[1]
            news["type"] = row[2]
            news["url"] = row[3]
            news["title"] = row[4]
            news["source"] = row[5]
            news["photourl"] = row[6]
            result.append(news)
            if i >= 40:
                break
        break
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getAttackMap(request, size=-1):
    conn, cur = createConnect()
    map = {}

    if size == -1:
        cur.execute("select time,attacker,attackIP,attackerGeo,targetGeo,attackType,port from attackmap ")
    else:
        type = random.randint(1, 11)
        cur.execute(
            "select time,attacker,attackIP,attackerGeo,targetGeo,attackType,port from attackmap where type = \'" + str(
                type) + "\'")
    results = cur.fetchall()
    for row in results:
        print(row)
        time = row[0]
        attack = {}
        attack["attacker"] = row[1]
        attack["attackIP"] = row[2]
        attack["attackGeo"] = row[3]
        attack["targetGeo"] = row[4]
        attack["attackType"] = row[5]
        attack["port"] = row[6]
        cur.execute("select latitude , longitude from location where place = \'" + attack["attackGeo"] + "\'")
        row = cur.fetchone()
        print(row)
        if row == None:
            attack["attackLatitude"] = 0
            attack["attackLongitude"] = 0
        else:
            attack["attackLatitude"] = row[0]
            attack["attackLongitude"] = row[1]
        cur.execute("select latitude , longitude from location where place = \'" + attack["targetGeo"] + "\'")
        row = cur.fetchone()
        print(row)
        if row == None:
            attack["targetLatitude"] = 0
            attack["targetLongitude"] = 0
        else:
            attack["targetLatitude"] = row[0]
            attack["targetLongitude"] = row[1]
        map[time] = attack
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(map))


def getAttacker(request):
    conn, cur = createConnect()
    result = {}
    cur.execute("select sourceIP, count(*) from conpot_log group by sourceIP order by date desc, time desc")
    results = cur.fetchall()
    for row in results:
        cur.execute("select city, country from GeoInfo where ip = '" + str(row[0]) + "'")
        otherInfo = cur.fetchone()
        if otherInfo == None:
            continue

        attacker = str(otherInfo[0]) + ", " + str(otherInfo[1])
        result[attacker] = row[1]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


# cur.execute("select GeoInfo.country, count(*) from conpot_log, GeoInfo where sourceIP = ip group by GeoInfo.country order by date desc, time desc")

def getAttackerCountry(request):
    conn, cur = createConnect()
    result = {}
    cur.execute(
        "select GeoInfo.country, count(*) from conpot_log, GeoInfo where sourceIP = ip group by GeoInfo.country order by date desc, time desc")
    results = cur.fetchall()
    for row in results:
        if str(row[0]) == 'China':
            attacker = "China Mainland"
        elif str(row[0]) == 'Taiwan':
            attacker = "Taiwan,China"
        else:
            attacker = str(row[0])
        result[attacker] = row[1]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getTarget(request):
    conn, cur = createConnect()
    result = {}
    cur.execute(
        "select count(*) times, GeoInfoTarget.city, GeoInfoTarget.country from conpot_log, GeoInfoTarget where destiIP = ip group by GeoInfoTarget.city, GeoInfoTarget.country order by date desc, time desc;")
    results = cur.fetchall()
    for row in results:
        target = str(row[1]) + ", " + str(row[2])
        result[target] = row[0]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getTargetCountry(request):
    conn, cur = createConnect()
    result = {}
    cur.execute(
        "select count(*) times, GeoInfoTarget.city from conpot_log, GeoInfoTarget where destiIP = ip group by GeoInfoTarget.city, GeoInfoTarget.country order by date desc, time desc;")
    results = cur.fetchall()
    for row in results:
        if str(row[1]) == 'None':
            target = 'Singapore,SIN'
        elif str(row[1]) == 'Long Keng':
            target = 'Hongkong,CN'
        elif str(row[1]) == 'San Mateo':
            target = 'San Mateo,USA'
        elif str(row[1]) == 'San Mateo':
            target = 'San Mateo,USA'
        else:
            target = str(row[1]) + ',CN'
        result[target] = row[0]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getAttackNum(request):
    conn, cur = createConnect()
    cur.execute("select count(*) from conpot_log;")
    row = cur.fetchone()
    result = row[0]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getType(request):
    conn, cur = createConnect()
    result = {}
    cur.execute("select protocol, count(*) times from conpot_log group by protocol order by times asc")
    results = cur.fetchall()
    for row in results:
        if row[0] in ['http/1.0', 'NULL', 'http/0.9']:
            pass
        else:
            result[str(str(row[0]).replace('/', '-'))] = row[1]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getTimeSequence(request):
    conn, cur = createConnect()
    result = []
    cur.execute("select date, time, count(*) from conpot_log group by date, time order by date asc, time asc")
    results = cur.fetchall()
    num = 0
    for row in results:
        num += int(row[2])
        r = {}
        r["date"] = str(row[0])
        r["time"] = str(row[1])
        r["total"] = num

        result.append(r)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


from knowledgeBase.models import vulnerability, instance


def VulIndex():
    result = {}
    index = {}
    year = thisyear
    month = thismonth
    day = thisday
    max = 0
    conn, cur = createConnect()
    cur.execute("select score,finddate from cve")
    list1 = cur.fetchall()
    # list=vulnerability.objects.values('level','date')
    for vulner in list1:
        i = 0
        time = vulner[1]
        if time == "":
            continue
        date = time[6:10] + time[11:13] + time[14:16]
        if vulner[0] == u'\u8f7b\u5fae':
            i = 2
        elif vulner[0] == u'\u4e2d\u7b49':
            i = 5
        elif vulner[0] == u'\u4e25\u91cd':
            i = 10
        else:
            i = 10
        if date in result:
            result[date] += i
        else:
            result[date] = i
    for number in result:
        if max < result[number]:
            max = result[number]
    # result = sorted(result.iteritems(),key=lambda d:d[0])
    for i in range(0, 100):
        loopyear = year
        loopmonth = month
        loopday = day
        if month < 10:
            tMonth = "0" + str(loopmonth)
        else:
            tMonth = str(loopmonth)
        if day < 10:
            tDay = "0" + str(loopday)
        else:
            tDay = str(day)
        date = str(year) + tMonth + tDay
        tindex = float(0)
        # print date
        for j in range(1, 101):
            if loopmonth < 10:
                theMonth = "0" + str(loopmonth)
            else:
                theMonth = str(loopmonth)
            if loopday < 10:
                theDay = "0" + str(loopday)
            else:
                theDay = str(loopday)
            loopdate = str(loopyear) + theMonth + theDay
            if loopdate in result:
                tindex += 100 * result[loopdate] / float(j * max)
            newdate = getDate(loopyear, loopmonth, loopday)
            loopyear = newdate["year"]
            loopmonth = newdate["month"]
            loopday = newdate["day"]
            # print loopdate
        index[date] = 100 - tindex * 5
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
    # index = sorted(index.iteritems(),key=lambda d:d[0])
    cur.close()
    conn.close()
    return index


def getVulIndex(request):
    result = VulIndex()
    return HttpResponse(json.dumps(result))


threaten = {}
for i in range(0, 100):
    threaten[i] = random.randint(30, 60)


def ThreatenIndex():
    result = {}
    year = thisyear
    month = thismonth
    day = thisday
    for i in range(0, 100):
        if month < 10:
            theMonth = "0" + str(month)
        else:
            theMonth = str(month)
        if (day < 10):
            theDay = "0" + str(day)
        else:
            theDay = str(day)
        date = str(year) + theMonth + theDay
        result[date] = 100 - threaten[i]
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
    return result


def getThreatenIndex(request):
    return HttpResponse(json.dumps(ThreatenIndex()))


def PublicIndex():
    conn, cur = createConnect()
    year = thisyear
    month = thismonth
    day = thisday
    result = {}
    rows = {}
    max1 = 0
    max2 = 0
    for i in range(0, 200):
        if month < 10:
            theMonth = "0" + str(month)
        else:
            theMonth = str(month)
        if (day < 10):
            theDay = "0" + str(day)
        else:
            theDay = str(day)

        date = str(year) + theMonth + theDay
        cur.execute("select count(*) from weibo where date = \'" + date + "\'")
        row1 = cur.fetchone()
        cur.execute("select count(*) from news where time = \'" + date + "\'")
        row2 = cur.fetchone()
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
        num = {}
        # num["weibo"] = row1[0]
        # num["news"] = row2[0]
        num["value"] = 0.7 * row2[0] + 0.3 * row1[0]
        num["date"] = date
        rows[i] = num
    for j in range(0, 100):
        num2 = rows[j]
        date = num2["date"]
        result[date] = 100
        for dayNumber in range(j, j + 100):
            thisNum = rows[dayNumber]
            if num2["value"] >= thisNum["value"]:
                result[date] -= 1
                # print row1[0] ,"**", row2[0] ,"******\n"
                # print num
                # rows.setdefault(date,num)
                # print rows
                # if max1 < row1[0]:
                #    max1 = row1[0]
                # if max2 < row2[0]:
                #    max2 = row2[0]

    """"print rows
    for key, value in rows.items():
        print value["weibo"], value["news"]
        if (max1 == 0):
            num1 = 0
        else:
            num1 = 0.3 * value["weibo"] / max1
        if (max2 == 0):
            num2 = 0
        else:
            num2 = 0.7 * value["news"] / max2
        result[key] = 100*(num1 + num2)"""""
    cur.close()
    conn.close()
    return result


def getIndex(request):
    result = {}
    result = PublicIndex()
    return HttpResponse(json.dumps(result))


def getSecurityIndex(request):
    year = thisyear
    month = thismonth
    day = thisday
    publicindex = PublicIndex()
    vulindex = VulIndex()
    threatenindex = ThreatenIndex()
    result = {}
    for i in range(0, 100):
        if month < 10:
            theMonth = "0" + str(month)
        else:
            theMonth = str(month)
        if (day < 10):
            theDay = "0" + str(day)
        else:
            theDay = str(day)
        date = str(year) + theMonth + theDay
        result[date] = (publicindex[date] + vulindex[date] + threatenindex[date]) / 3
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
    return HttpResponse(json.dumps(result))


def getAllIndex(request):
    result = {}
    result["PublicIndex"] = PublicIndex()
    result["VulIndex"] = VulIndex()
    result["ThreatenIndex"] = ThreatenIndex()
    year = thisyear
    month = thismonth
    day = thisday
    result["SecurityIndex"] = {}
    for i in range(0, 100):
        if month < 10:
            theMonth = "0" + str(month)
        else:
            theMonth = str(month)
        if (day < 10):
            theDay = "0" + str(day)
        else:
            theDay = str(day)
        date = str(year) + theMonth + theDay
        result["SecurityIndex"][date] = (result["PublicIndex"][date] + result["VulIndex"][date] +
                                         result["ThreatenIndex"][date]) / 3
        newdate = getDate(year, month, day)
        year = newdate["year"]
        month = newdate["month"]
        day = newdate["day"]
    return HttpResponse(json.dumps(result))


def getConpots(request):
    conn, cur = createConnect()
    result = []
    cur.execute("select * from conpot_log_1 ORDER BY time DESC")
    results = cur.fetchall()
    for row in results:
        news = {}
        news["date"] = str(row[0])
        news["time"] = str(row[1])
        news["function_id"] = row[2]
        news["protocol"] = row[3]
        news["request"] = row[4]
        news["destiIP"] = row[5]
        news["sourcePort"] = row[6]
        news["DestiPort"] = row[7]
        news["slaveID"] = row[8]
        news["sourceIP"] = row[9]
        news["response"] = row[10]
        news["country"] = row[11]
        news["subdivision"] = row[12]
        news["city"] = row[13]
        news["coordinate"] = row[14]
        result.append(news)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def get_Conpots(request):
    conn, cur = createConnect()
    result = []
    cur.execute("select * from conpot_log order by date desc, time desc")
    results = cur.fetchall()
    for row in results:
        news = {}

        cur.execute("select * from GeoInfo where ip = '" + str(row[9]) + "'")
        attacker = cur.fetchone()
        cur.execute("select * from GeoInfoTarget where ip = '" + str(row[5]) + "'")
        target = cur.fetchone()
        cur.execute("select * from GeoInfoOrg where ip = '" + str(row[9]) + "'")
        attackerOrg = cur.fetchone()
        cur.execute("select * from GeoInfoTargetOrg where ip = '" + str(row[5]) + "'")
        targetOrg = cur.fetchone()

        if attacker == None or target == None or attackerOrg == None or targetOrg == None:
            continue

        news["targetGeo"] = str(target[3]) + ", " + str(target[1])
        s = str(target[4]).split(",")
        news["targetLatitude"] = float(s[0][1: len(s[0])])
        news["targetLongitude"] = float(s[1][0: len(s[1]) - 1])
        # till 10

        news["attacker"] = str(attackerOrg[2])
        #
        news["attackIP"] = str(row[9])

        news["attackType"] = str(row[3].replace('/', '-'))

        news["attackGeo"] = str(attacker[3]) + ", " + str(attacker[1])

        t = str(attacker[4]).split(",")  # t is : "(????" and "????)"
        news["attackLatitude"] = float(t[0][1: len(t[0])])  # give up the first left parenthesis
        news["attackLongitude"] = float(t[1][0: len(t[1]) - 1])  # give up the last right parenthesis

        news["port"] = row[7]

        news["dateTime"] = str(row[0]) + " " + str(row[1])

        result.append(news)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def get_Conpots1(request, date_, limit_):
    conn, cur = createConnect()
    result = []
    cur.execute(
        'select * from conpot_log where date <= "' + str(date_) + '" order by date desc, time desc limit ' + str(
            limit_))
    results = cur.fetchall()
    for row in results:
        news = {}

        cur.execute("select * from GeoInfo where ip = '" + str(row[9]) + "'")
        attacker = cur.fetchone()
        cur.execute("select * from GeoInfoTarget where ip = '" + str(row[5]) + "'")
        target = cur.fetchone()
        cur.execute("select * from GeoInfoOrg where ip = '" + str(row[9]) + "'")
        attackerOrg = cur.fetchone()
        cur.execute("select * from GeoInfoTargetOrg where ip = '" + str(row[5]) + "'")
        targetOrg = cur.fetchone()

        if attacker == None or target == None or attackerOrg == None or targetOrg == None:
            continue

        news["targetGeo"] = str(target[3]) + ", " + str(target[1])
        s = str(target[4]).split(",")
        news["targetLatitude"] = float(s[0][1: len(s[0])])
        news["targetLongitude"] = float(s[1][0: len(s[1]) - 1])
        # till 10

        news["attacker"] = str(attackerOrg[2])
        #
        news["attackIP"] = str(row[9])

        news["attackType"] = str(row[3].replace('/', '-'))

        news["attackGeo"] = str(attacker[3]) + ", " + str(attacker[1])

        t = str(attacker[4]).split(",")  # t is : "(????" and "????)"
        news["attackLatitude"] = float(t[0][1: len(t[0])])  # give up the first left parenthesis
        news["attackLongitude"] = float(t[1][0: len(t[1]) - 1])  # give up the last right parenthesis

        news["port"] = row[7]

        news["dateTime"] = str(row[0]) + " " + str(row[1])

        result.append(news)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def get_Conpots2(request, date_, limit_):
    conn, cur = createConnect()
    result = []
    cur.execute(
        'select * from conpot_log where date <= "' + str(date_) + '" order by date desc, time desc limit ' + str(
            limit_))
    results = cur.fetchall()
    temp_type = ""
    temp_count = 0
    for row in results:
        news = {}

        cur.execute("select * from GeoInfo where ip = '" + str(row[9]) + "'")
        attacker = cur.fetchone()
        cur.execute("select * from GeoInfoTarget where ip = '" + str(row[5]) + "'")
        target = cur.fetchone()
        cur.execute("select * from GeoInfoOrg where ip = '" + str(row[9]) + "'")
        attackerOrg = cur.fetchone()
        cur.execute("select * from GeoInfoTargetOrg where ip = '" + str(row[5]) + "'")
        targetOrg = cur.fetchone()

        if attacker == None or target == None or attackerOrg == None or targetOrg == None:
            continue

        tp = str(row[3].replace('/', '-'))
        if tp != temp_type:
            temp_count = 1
            temp_type = tp
        else:
            if temp_count < 5:
                temp_count += 1
            else:
                continue

        news["attackType"] = tp

        news["targetGeo"] = str(target[3]) + ", " + str(target[1])
        s = str(target[4]).split(",")
        news["targetLatitude"] = float(s[0][1: len(s[0])])
        news["targetLongitude"] = float(s[1][0: len(s[1]) - 1])
        # till 10

        news["attacker"] = str(attackerOrg[2])
        #
        news["attackIP"] = str(row[9])

        news["attackGeo"] = str(attacker[3]) + ", " + str(attacker[1])

        t = str(attacker[4]).split(",")  # t is : "(????" and "????)"
        news["attackLatitude"] = float(t[0][1: len(t[0])])  # give up the first left parenthesis
        news["attackLongitude"] = float(t[1][0: len(t[1]) - 1])  # give up the last right parenthesis

        news["port"] = row[7]

        news["dateTime"] = str(row[0]) + " " + str(row[1])

        result.append(news)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


global a
a = 7641


def getStatistics(request):
    result = {}
    conn, cur = createConnect()
    # global a
    # num=random.randint(1, 50)
    # a+=num
    cur.execute("select count(*) from conpot_log")
    row = cur.fetchone()
    result["attack"] = row[0]
    cur.execute("select count(*) from weibo")
    row = cur.fetchone()
    result["public"] = row[0]
    cur.execute("select count(*) from news")
    row = cur.fetchone()
    result["public"] += row[0]
    result["vul"] = 0
    result["device"] = 0
    list = vulnerability.objects.values()
    for vulner in list:
        result["vul"] += 1
    cur.execute("select count(*) from cve")
    row = cur.fetchone()
    result["vul"] += row[0]
    list = instance.objects.values()
    for dev in list:
        result["device"] += 1
    cur.execute('select count(*) from ips')
    row = cur.fetchone()
    result["suspiciousIP"] = row[0]
    cur.execute('select count(*) from shoplist')
    row = cur.fetchone()
    result["shoplist"] = row[0]
    cur.execute('select count(*) from paper')
    row = cur.fetchone()
    result["paper"] = row[0]
    result["professional_blog_news"] = 0
    blog_news_list = ['blogs', 'cnblogs', 'icssnews', 'cnicssnews']
    i = 0
    while i < 4:
        cur.execute("select count(id) from " + blog_news_list[i] + ';')
        row = cur.fetchone()
        result['professional_blog_news'] = result['professional_blog_news'] + row[0]
        i = i + 1
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


# import threatcrowd


def getThreatCrowd(request, type, obj):
    results = threatcrowd.Threat(type, obj)
    return HttpResponse(json.dumps(results))


# import weiboheat


def getWeiboHeat(request, date_):
    conn, cur = createConnect()
    results = []
    count = 0
    fansnum = ['fans<100', 'fans between 100 and 1000 ', 'fans between 1000 and 5000', 'fans between 5000 and 10000',
               'fans between 10000 and 100000', 'fans between 100000 and 1000000', 'fans>1000000']
    while count < 22:
        week = {}
        last_date_of_this_week = weiboheat.DateOfNweeksBefore(date_, count)
        week['date'] = last_date_of_this_week
        dates_of_this_week = weiboheat.WeekBeforeDate(last_date_of_this_week)
        j = 1
        maximun = 0
        while j < 8:
            cur.execute(
                "SELECT count(*) FROM ics.weibo where date in (" + str(dates_of_this_week).replace('[', '').replace(']',
                                                                                                                    '') + ") and " +
                fansnum[j - 1])
            row = cur.fetchone()
            heatevents = int(row[0])
            week['heatevents' + str(j)] = heatevents
            if heatevents > maximun:
                maximun = heatevents
            j = j + 1
        week['maximun'] = maximun
        results.append(week)
        count = count + 1
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(results))


def getIpStatistic(request):
    conn, cur = createConnect()
    results = []
    result = {}
    cur.execute("select kind,count(kind) from ips group by kind")
    rows = cur.fetchall()
    for row in rows:
        kind = row[0]
        num = int(row[1])
        result[kind] = num
    cur.execute('select count(*) from ics.ips')
    row = cur.fetchone()
    result['total'] = int(row[0])
    results.append(result)

    cur.close()
    conn.close()
    return HttpResponse(json.dumps(results))


####################### update on 2017.01.16 by lizihan ########################################
def getPageNum(request, kind, num):
    conn, cur = createConnect()
    result = []
    cur.execute("select count(id) from " + kind)
    # kind=blogsӢ�Ĳ���/kind=cnblogs���Ĳ���/kind=icssnewsӢ������
    results = cur.fetchall()
    for row in results:
        pagenum = {}
        if int(row[0]) % int(num) == 0:
            pagenum["pagenum"] = int(row[0]) / int(num)
        else:
            pagenum["pagenum"] = int(row[0]) / int(num) + 1
        result.append(pagenum)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getBlogAndNews(request, kind, time, num):
    conn, cur = createConnect()
    result = []
    if (time == '0'):
        timeSearch = ""
    else:
        timeSearch = " where time = " + str(time)
    if (num == '0'):
        limit = ""
    else:
        limit = " limit " + str(num)
    # kind=blogsӢ�Ĳ���/kind=cnblogs���Ĳ���/kind=icssnewsӢ������
    cur.execute(
        "select id,source,title,author,time,article,url,curtime,categories,tags,aboutauthor from " + kind + timeSearch + " order by time desc,source,id asc" + limit)
    results = cur.fetchall()
    for row in results:
        data = {}
        data["id"] = row[0]
        data['source'] = row[1]
        data['title'] = row[2]
        data['author'] = row[3]
        data['time'] = row[4]
        data['article'] = row[5]
        data['url'] = row[6]
        data['curtime'] = row[7]
        data['categories'] = row[8]
        data['tags'] = row[9]
        data['aboutauthor'] = row[10]
        result.append(data)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def getBlogAndNews4Page(request, kind, time, page, num):
    conn, cur = createConnect()
    result = []
    if (time == '0'):
        timeSearch = ""
    else:
        timeSearch = " where time = " + str(time)
    if int(page) < 0:
        startid = 0
    else:
        startid = (int(page) - 1) * int(num)
    if int(num) < 0:
        num = '0'
    limit = " limit " + str(startid) + " , " + str(num)
    # kind=blogsӢ�Ĳ���/kind=cnblogs���Ĳ���/kind=icssnewsӢ������
    cur.execute(
        "select id,source,title,author,time,article,url,curtime,categories,tags,aboutauthor from " + kind + timeSearch + " order by time desc,source,id asc" + limit)
    results = cur.fetchall()
    for row in results:
        data = {}
        data["id"] = row[0]
        data['source'] = row[1]
        data['title'] = row[2]
        data['author'] = row[3]
        data['time'] = row[4]
        data['article'] = row[5]
        data['url'] = row[6]
        data['curtime'] = row[7]
        data['categories'] = row[8]
        data['tags'] = row[9]
        data['aboutauthor'] = row[10]
        result.append(data)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


############################################################################################
def getConpots_info_ics(request, date_, limit_):
    conn, cur = createConnect()
    result = []
    cur.execute(
        'select * from conpot_log where date <= "' + str(
            date_) + '"' + ' and protocol not like "http%" and protocol <>"NULL"  order by date desc, time desc limit ' + str(
            limit_))
    results = cur.fetchall()
    temp_type = ""
    temp_count = 0
    for row in results:
        news = {}

        cur.execute("select * from GeoInfo where ip = '" + str(row[9]) + "'")
        attacker = cur.fetchone()
        cur.execute("select * from GeoInfoTarget where ip = '" + str(row[5]) + "'")
        target = cur.fetchone()
        cur.execute("select * from GeoInfoOrg where ip = '" + str(row[9]) + "'")
        attackerOrg = cur.fetchone()
        cur.execute("select * from GeoInfoTargetOrg where ip = '" + str(row[5]) + "'")
        targetOrg = cur.fetchone()

        if attacker == None or target == None or attackerOrg == None or targetOrg == None:
            continue

        tp = str(row[3].replace('/', '-'))
        if tp != temp_type:
            temp_count = 1
            temp_type = tp
        else:
            if temp_count < 5:
                temp_count += 1
            else:
                continue

        news["attackType"] = tp

        news["targetGeo"] = str(target[3]) + ", " + str(target[1])
        s = str(target[4]).split(",")
        news["targetLatitude"] = float(s[0][1: len(s[0])])
        news["targetLongitude"] = float(s[1][0: len(s[1]) - 1])
        # till 10

        news["attacker"] = str(attackerOrg[2])
        #
        news["attackIP"] = str(row[9])

        news["attackGeo"] = str(attacker[3]) + ", " + str(attacker[1])

        t = str(attacker[4]).split(",")  # t is : "(????" and "????)"
        news["attackLatitude"] = float(t[0][1: len(t[0])])  # give up the first left parenthesis
        news["attackLongitude"] = float(t[1][0: len(t[1]) - 1])  # give up the last right parenthesis

        news["port"] = row[7]

        news["dateTime"] = str(row[0]) + " " + str(row[1])

        result.append(news)
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


## update the quantity of each public news source 2017.3.1
def getQuantityOfEachSource(request):
    result = {}
    conn, cur = createConnect()
    cur.execute("select count(*) from ics.yqmsweixin")
    row = cur.fetchone()
    result["Weixin"] = row[0]
    cur.execute("select count(*) from weibo")
    row = cur.fetchone()
    result["Weibo"] = row[0]
    cur.execute("select count(*) from yqmsnews")
    row = cur.fetchone()
    result["Zhuanyexinwen"] = row[0]
    cur.execute("select count(*) from yqmsblog")
    row = cur.fetchone()
    result["Zhuanyeboke"] = row[0]
    cur.close()
    conn.close()
    return HttpResponse(json.dumps(result))


def syn_cve(request):
    """
    用于同步cve数据给其他部署的系统
    参数d：指定返回此日期之后的数据，格式为YYYY-MM-DD
    :param request:
    :return:
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Not support method'})

    d = request.GET.get('d')

    if not d:
        return JsonResponse({'error': 'Invalid parameter'})

    try:
        conn, cursor = createConnect()
        try:

            sql = "select id,num,score,secrecy,integrity," \
                  "usability,complexity,vectorofattack,identify,kind," \
                  "cpe,finddate,summary from cve where finddate >= %s"

            param = "发布时间 :%s 00:00:00" % d

            cursor.execute(sql, (param,))
            results = cursor.fetchall()

            cve_list = list()
            for row in results:
                cve = dict()
                cve["id"] = row[0]
                cve["num"] = row[1]
                cve["score"] = row[2]
                cve["secrecy"] = row[3]
                cve["integrity"] = row[4]
                cve["usability"] = row[5]
                cve["complexity"] = row[6]
                cve["vectorofattack"] = row[7]
                cve["identify"] = row[8]
                cve["kind"] = row[9]
                cve["cpe"] = row[10]
                cve["finddate"] = row[11]
                cve["summary"] = row[12]
                cve_list.append(cve)

        finally:
            cursor.close()
            conn.close()

        syn_data = {"result": cve_list}
        return JsonResponse(syn_data, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': 'System Error: %s' % e})


def syn_conpot_log(request):
    """
    用于同步conpot_log数据给其他部署的系统
    参数d：指定返回此日期之后的数据，格式为YYYY-MM-DD
    :param request:
    :return:
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Not support method'})

    d = request.GET.get('d')

    if not d:
        return JsonResponse({'error': 'Invalid parameter'})

    try:
        conn, cursor = createConnect()
        try:

            sql = "select date,time,function_id,protocol,request," \
                  "destiIP,sourcePort,DestiPort,slaveID,sourceIP," \
                  "response,country,subdivision,city,coordinate " \
                  "from conpot_log where date >= %s"

            print("sql=%s" % sql)
            print("param=%s" % d)
            cursor.execute(sql, (d,))
            results = cursor.fetchall()

            data_list = list()
            for row in results:
                item = dict()
                item["date"] = _to_str(row[0])
                item["time"] = _to_str(row[1])
                item["function_id"] = row[2]
                item["protocol"] = row[3]
                item["request"] = row[4]
                item["destiIP"] = row[5]
                item["sourcePort"] = row[6]
                item["DestiPort"] = row[7]
                item["slaveID"] = row[8]
                item["sourceIP"] = row[9]
                item["response"] = row[10]
                item["country"] = row[11]
                item["subdivision"] = row[12]
                item["city"] = row[13]
                item["coordinate"] = row[14]
                data_list.append(item)

        finally:
            cursor.close()
            conn.close()

        print("result size: %s" % len(data_list))
        syn_data = {"result": data_list}
        return JsonResponse(syn_data, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': 'System Error: %s' % e})


def _to_str(msg):
    if msg is None:
        return None

    if msg:
        return str(msg)
    return ''
	
	
def syn_geo_info(request):
    """
    用于同步conpot_log数据给其他部署的系统
    参数d：指定返回此日期之后的数据，格式为YYYY-MM-DD
    :param request:
    :return:
    """

    try:
        conn, cursor = createConnect()
        try:

            sql = "select ip,country,subdivision,city,coordinate from GeoInfo"

            print("sql=%s" % sql)
            count=cursor.execute(sql)
            results = cursor.fetchall()
			
            data_list = list()
            for row in results:
                item = dict()
                item["ip"] = row[0]
                item["country"] = row[1]
                item["subdivision"] = row[2]
                item["city"] = row[3]
                item["coordinate"] = row[4]
                data_list.append(item)

        finally:
            cursor.close()
            conn.close()

        print("result size: %s" % len(data_list))
        syn_data = {"result": data_list}
        return JsonResponse(syn_data, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': 'System Error: %s' % e})

		
def syn_geo_info_target(request):
    """
    用于同步conpot_log数据给其他部署的系统
    参数d：指定返回此日期之后的数据，格式为YYYY-MM-DD
    :param request:
    :return:
    """

    try:
        conn, cursor = createConnect()
        try:

            sql = "select ip,country,subdivision,city,coordinate from GeoInfo"

            print("sql=%s" % sql)
            cursor.execute(sql)
            results = cursor.fetchall()

            data_list = list()
            for row in results:
                item = dict()
                item["ip"] = row[0]
                item["country"] = row[1]
                item["subdivision"] = row[2]
                item["city"] = row[3]
                item["coordinate"] = row[4]
                data_list.append(item)

        finally:
            cursor.close()
            conn.close()

        print("result size: %s" % len(data_list))
        syn_data = {"result": data_list}
        return JsonResponse(syn_data, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': 'System Error: %s' % e})
def syn_geo_info_org(request):
    """
    用于同步conpot_log数据给其他部署的系统
    参数d：指定返回此日期之后的数据，格式为YYYY-MM-DD
    :param request:
    :return:
    """
    try:
        conn, cursor = createConnect()
        try:

            sql = "select ip,isp,organization " \
                      "from GeoInfoOrg"

            print("sql=%s" % sql)
            cursor.execute(sql)
            results = cursor.fetchall()

            data_list = list()
            for row in results:
                item = dict()
                item["ip"] = row[0]
                item["isp"] = row[1]
                item["organization"] = row[2]
                data_list.append(item)

        finally:
            cursor.close()
            conn.close()

        print("result size: %s" % len(data_list))
        syn_data = {"result": data_list}
        return JsonResponse(syn_data, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': 'System Error: %s' % e})
		
def syn_geo_info_target_org(request):
    """
    用于同步conpot_log数据给其他部署的系统
    参数d：指定返回此日期之后的数据，格式为YYYY-MM-DD
    :param request:
    :return:
    """

    try:
        conn, cursor = createConnect()
        try:

            sql = "select ip,isp,organization " \
                      "from GeoInfoOrg"

            print("sql=%s" % sql)
            cursor.execute(sql)
            results = cursor.fetchall()

            data_list = list()
            for row in results:
                item = dict()
                item["ip"] = row[0]
                item["isp"] = row[1]
                item["organization"] = row[2]
                data_list.append(item)

        finally:
            cursor.close()
            conn.close()

        print("result size: %s" % len(data_list))
        syn_data = {"result": data_list}
        return JsonResponse(syn_data, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': 'System Error: %s' % e})