#!/usr/bin python
# -*- coding:utf-8 -*-

import json
import sys
import threading

from client import GremlinRestClient

from data_preprocess import *


class EImport(object):
    # Configuration parameters
    batchNum = 50
    threadNum = 4
    threadLock = threading.Lock()
    sleepTime = 0.005
    vertices = {}

    # Debug parameter
    importRecord = []
    speedPrintInterval = 1
    ECount = 0

    def __init__(self, edges, graph, server):
        self.edges = edges
        self.graph = json.load(file("properties.json"))[graph]
        self.JSON = json.load(file("%s.json" % graph))
        self.server = server

    def execute(self):
        """
        EType = set()
        for edge in self.edges:
            EType.add(edge['type'])
        VType = set()
        for edge in EType:
            VType.add("v_%s" % (self.graph, self.JSON['edges'][edge]['vertices'][0]))
            VType.add("v_%s" % (self.graph, self.JSON['edges'][edge]['vertices'][1]))
        
        #获取所有点的id, label, name，供边快速插入
        print "get the information of vertices..."
        for type in VType:
            response = GremlinRestClient(self.server).execute("%s.V().hasLabel('%s').union(properties('name').value(), id())" % (self.graph, type))[1]
            for i in range(len(response)/2):
                self.vertices[(type, response[2*i])] = response[2*i+1]
        """
        print("edges import begin...")
        begin = time.time()
        # 多线程插入
        threadList = []
        for i in range(0, self.threadNum):
            thread = EThread(self)
            threadList.append(thread)
            thread.start()
        for thread in threadList:
            thread.join()
        end = time.time()

        print("edges import finish, sum: %d, time: %fs, avgSpeed: %de/s" % (
        self.ECount, end - begin, int(self.ECount / (end - begin))))


class EThread(threading.Thread):
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
                    print("%dk %de/s" % ((int(parent.ECount) / 1000), int(batchCount / (now - parent.importRecord[0][1]))))
                    parent.importRecord = []

            if len(parent.edges) == parent.ECount:
                parent.threadLock.release()
                break

            end = parent.batchNum
            if self.slowStart > 0 and end > 10:
                end = end / self.slowStart / 2
                self.slowStart -= 1
            end = min(len(parent.edges) - parent.ECount, end)
            list = parent.edges[parent.ECount: parent.ECount + end]
            parent.ECount += end

            parent.importRecord.append([end, time.time()])

            parent.threadLock.release()

            self.EScript(list)

    def EScript(self, list):

        timeA = time.time()

        parent = self.parent
        script = ""
        lastS = ""
        lastD = ""
        bindings = {}

        # id导入法
        verLabelDic = {}
        verNameDic = {}
        verIdDic = {}
        edgeLabelDic = {}
        proKeyDic = {}
        proValueDic = {}

        jsonV = parent.JSON['vertices']
        jsonE = parent.JSON['edges']
        for item in list:
            e = jsonE[item['type']]

            srcVName = item['srcV']
            if verNameDic.has_key(srcVName):
                script += "%s.V().has('name', n%d).hasLabel('v_%s').next()." % (
                parent.graph, verNameDic[srcVName], e['vertices'][0])
            else:
                script += "%s.V().has('name', n%d).hasLabel('v_%s').next()." % (
                parent.graph, len(verNameDic), e['vertices'][0])
                bindings["n%d" % len(verNameDic)] = srcVName
                verNameDic[srcVName] = len(verNameDic)

            edgeLabel = e['key']
            script += "addEdge('%s', " % edgeLabel

            dstVName = item['dstV']
            if verNameDic.has_key(dstVName):
                script += "%s.V().has('name', n%d).hasLabel('v_%s').next(), " % (
                parent.graph, verNameDic[dstVName], e['vertices'][1])
            else:
                script += "%s.V().has('name', n%d).hasLabel('v_%s').next(), " % (
                parent.graph, len(verNameDic), e['vertices'][1])
                bindings["n%d" % len(verNameDic)] = dstVName
                verNameDic[dstVName] = len(verNameDic)

            properties = e['properties']
            for key, value in item.items():
                if key in properties:
                    script += "'%s', " % key
                    if proValueDic.has_key(value):
                        script += "pV%d, " % proValueDic[value]
                    else:
                        script += "pV%d, " % len(proValueDic)
                        bindings["pV%d" % len(proValueDic)] = value
                        proValueDic[value] = len(proValueDic)

                        # script += "'%s', '%s', " % (key, value)
            script += ");\n"
        """
        print script
        print bindings
        print "\n"
        """
        timeB = time.time()
        try:
            GremlinRestClient(parent.server).execute(script, bindings)
        except:
            print(script)
            print(bindings)
            print("\n")
        timeC = time.time()

        # print script
        # print bindings
        # print timeB-timeA, timeC-timeB, (timeB-timeA) / (timeC-timeA) * 100,

        time.sleep(parent.sleepTime)
