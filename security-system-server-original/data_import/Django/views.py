import json
import sys

from client import GremlinRestClient
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

reload(sys)
sys.setdefaultencoding("utf-8")
import threading

JSON = json.load(file("/usr/local/security-system-server/security_system/queryAPI/properties.json"))
server = JSON["server"]
graphs = JSON["graphs"]
proConvert = JSON["proConvert"]

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

    # check whether srcID and dstID exist in database
    script = "%s.V(%s).count()" % (abstract, dic['srcID'])
    if GremlinRestClient(server).execute(script)[1][0] == 0:
        return HttpResponse(json.dumps({"message": "srcID doesn't exist in database"}))
    script = "%s.V(%s).count()" % (abstract, dic['dstID'])
    if GremlinRestClient(server).execute(script)[1][0] == 0:
        return HttpResponse(json.dumps({"message": "dstID doesn't exist in database"}))

    # insert edge into database
    script = "%s.V(%s).next().addEdge('%s', %s.V(%s).next(), " % (
    abstract, dic['srcID'], labelConvert(False, True, dic['type']), abstract, dic['dstID'])
    pro = graphs[graph]["properties"]
    for key, value in dic.items():
        if key in pro:
            script += "'%s', '%s', " % (key, value)
    script += ")"
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
    script = "%s.V(%s).both()%s.unique()" % (abstract, dic['id'], VLimit)
    response = GremlinRestClient(server).execute(script)[1]
    if len(response) == 0:
        return HttpResponse(json.dumps({'nodes': [], 'edges': []}))
    result['nodes'] = convertNodes(graph, response, [])

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
