#!/usr/bin python
# -*- coding:utf-8 -*-

import json
import sys
import threading

from client import GremlinRestClient

from data_preprocess import *

reload(sys)
sys.setdefaultencoding("utf-8")


class VImport(object):
    # Configuration parameters
    batchNum = 100
    threadNum = 8
    threadLock = threading.Lock()
    sleepTime = 0.005

    # Debug parameter
    importRecord = []
    speedPrintInterval = 1
    VCount = 0

    def __init__(self, vertices, graph, server):
        self.vertices = vertices
        self.Graph = graph
        self.graph = json.load(file("properties.json"))[graph]
        self.JSON = json.load(file("%s.json" % graph))
        self.server = server

    def execute(self):
        if len(self.vertices) == 0:
            return
        time.sleep(0.5)
        self.__removeDuplVer()
        print("vertices import begin...")
        time.sleep(0.5)

        # 多线程插入
        begin = time.time()
        threadList = []
        for i in range(0, self.threadNum):
            thread = VThread(self)
            threadList.append(thread)
            thread.start()
        for thread in threadList:
            thread.join()
        end = time.time()

        print("vertices import finish, sum: %d, time: %fs, avgSpeed: %dv/s" % (
        self.VCount, end - begin, int(self.VCount / (end - begin))))

    def __removeDuplVer(self):
        print("remove duplicate vertices...")
        VType = set()
        for vertex in self.vertices:
            VType.add(vertex['type'])

        existed = set()
        for type in VType:
            response = \
            GremlinRestClient(self.server).execute("%s.V().hasLabel('v_%s').values('name')" % (self.graph, type))[1]
            for vertex in response:
                existed.add((type, str(vertex)))
        tempList = []
        for item in self.vertices:
            if (str(item['type']), str(item['name'])) not in existed:
                tempList.append(item)
        self.vertices = tempList


class VThread(threading.Thread):
    slowStart = 4

    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent

    def run(self):
        parent = self.parent
        while True:
            parent.threadLock.acquire()

            # Debug speed
            if len(parent.importRecord) > 0:
                now = time.time()
                if now - parent.importRecord[0][1] >= parent.speedPrintInterval:
                    batchCount = 0
                    for recode in parent.importRecord:
                        batchCount += recode[0]
                    print("%dk %dv/s" % ((int(parent.VCount) / 1000), int(batchCount / (now - parent.importRecord[0][1]))))
                    parent.importRecord = []

            if len(parent.vertices) == parent.VCount:
                parent.threadLock.release()
                break

            end = parent.batchNum
            if self.slowStart > 0 and end > 10:
                end = end / self.slowStart
                self.slowStart -= 1
            end = min(len(parent.vertices) - parent.VCount, end)
            list = parent.vertices[parent.VCount: parent.VCount + end]
            parent.VCount += end
            parent.importRecord.append([end, time.time()])

            parent.threadLock.release()

            self.VScript(list)

    # edit gremlin statements, insert into the database
    def VScript(self, list):
        parent = self.parent
        script = ""
        bindings = {}

        verTypeDic = {}
        proKeyDic = {}
        proValueDic = {}

        jsonV = parent.JSON['vertices']
        for item in list:
            v = jsonV[item['type']]

            script += "%s.addVertex(label, '%s', " % (parent.Graph, v['key'])

            properties = v['properties']
            for key, value in item.items():
                if key in properties:
                    script += "'%s', " % key
                    if proValueDic.has_key(value):
                        script += "pV%d, " % proValueDic[value]
                    else:
                        script += "pV%d, " % len(proValueDic)
                        bindings["pV%d" % len(proValueDic)] = value
                        proValueDic[value] = len(proValueDic)
            script += ");\n"

        GremlinRestClient(parent.server).execute(script, bindings)
        time.sleep(parent.sleepTime)
