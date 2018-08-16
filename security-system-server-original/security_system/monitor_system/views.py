#!/usr/bin python
# -*- coding:utf-8 -*-

import json
import os

from django.http import HttpResponse


# reload(sys)
# sys.setdefaultencoding("utf-8")

def getMonitorInfo(request):
    # cache data
    nodes = set()

    # return data
    data = {}
    data["nodes"] = []
    data["edges"] = {}

    categories = ["normal", "abnormal"]
    for category in categories:
        categoryData = {}
        categoryDir = os.path.join("/usr/local/security-system-server/security_system/monitor_system/displayData",
                                   category)
        fileList = os.listdir(categoryDir)
        for i in range(len(fileList)):
            fileData = []
            for line in file(os.path.join(categoryDir, fileList[i])):
                dic = json.loads(line)
                if "sa" in dic and "da" in dic and "sp" in dic and "dp" in dic:
                    srcID = str(dic["sa"]) + ":" + str(dic["sp"])
                    dstID = str(dic["da"]) + ":" + str(dic["dp"])
                    if srcID not in nodes:
                        nodes.add(srcID)
                    if dstID not in nodes:
                        nodes.add(dstID)
                    del dic["sa"]
                    del dic["da"]
                    del dic["sp"]
                    del dic["dp"]
                    dic["source"] = srcID
                    dic["target"] = dstID
                    dic["id"] = srcID + "-----" + dstID
                    dic["type"] = "flow"
                    fileData.append(dic)
            categoryData["file" + str(i)] = {}
            categoryData["file" + str(i)]["fileName"] = fileList[i]
            categoryData["file" + str(i)]["data"] = fileData
        data["edges"][category] = categoryData
    for node in nodes:
        splitList = node.split(':')
        dic = {}
        dic["id"] = node
        dic["ip"] = splitList[0]
        dic["port"] = splitList[1]
        dic["type"] = "ip"
        data["nodes"].append(dic)
    return HttpResponse(json.dumps(data))
