#!/usr/bin python
# -*- coding:utf-8 -*-

import sys

from EImport import EImport
from VImport import VImport
from data_formatting_knowledgeBase import *
from data_preprocess_knowledgeBase import *

from data_preprocess import *


class DataImport(object):
    def __init__(self, filePath, server="http://10.1.1.48:8182"):
        self.server = server
        self.filePath = filePath

    def execute(self, graph, type, threadLock=None):
        print("%s_%s %s import process begin..." % (graph, type, self.filePath))
        if graph == "graph1":
            object = graph1_DataPreProcess(self.filePath)
        elif graph == "graph2":
            object = graph2_DataPreProcess(self.filePath)
        elif graph == "knowledgeBase":
            object = knowledgeBase_DataPreProcess(self.filePath)
        elif graph == "knowledgeBaseSQL":
            object = knowledgeBase_FormattingProcess(self.filePath)
            return getattr(object, "%s_preprocess" % type)()

        vertices, edges = getattr(object, "%s_preprocess" % type)()
        print("%d vertices, %d edges" % (len(vertices), len(edges)))
        print("preprocess finish")

        if threadLock != None:
            threadLock.acquire()
        VImport(vertices, graph, self.server).execute()
        if threadLock != None:
            threadLock.release()
        time.sleep(1)
        EImport(edges, graph, self.server).execute()
        print("\n")
