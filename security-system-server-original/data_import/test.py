#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import os
import sys
import threading

reload(sys)
sys.setdefaultencoding("utf-8")

JSON = json.load(file("knowledgeBase.json"))["vertices"]


def graph1Import(graph):
    taskList.append(("data/graph1/flow.txt", graph, "flow"))
    taskList.append(("data/graph1/jsp.txt", graph, "jsp"))


def graph2Import(graph):
    taskList.append(("data/graph2/dns.txt", graph, "dns"))
    taskList.append(("data/graph2/depmt.txt", graph, "depmt"))
    taskList.append(("data/graph2/download.txt", graph, "download"))
    pathFlow = "data/graph2/flow"
    for item in os.listdir(pathFlow):
        if item.startswith("flow") and item.endswith(".txt"):
            path = os.path.join(pathFlow, item)
            taskList.append((path, graph, "flow"))


def knowledgeBaseImport(graph):
    DataImport(["data/knowledgeBase/vendor.txt"]).execute(graph, "vendor")
    DataImport(["data/knowledgeBase/protocol.txt"]).execute(graph, "protocol")
    DataImport(["data/knowledgeBase/done.txt"]).execute(graph, "deviceVendor")
    DataImport(["data/knowledgeBase/vul.txt", "data/knowledgeBase/vendor.txt"]).execute(graph, "vulnerability")
    DataImport(["data/knowledgeBase/Camera.json"]).execute(graph, "camera_instance")

    pathZoomeyeInstance = "data/knowledgeBase/zoomeye"
    for item in os.listdir(pathZoomeyeInstance):
        if item.endswith(".json"):
            path = os.path.join(pathZoomeyeInstance, item)
            DataImport([path, "data/knowledgeBase/vendor.txt"]).execute(graph, "zoomeye_instance")

    pathDeviceTypeInstance = "data/knowledgeBase/deviceType"
    for item in os.listdir(pathDeviceTypeInstance):
        if item.endswith(".txt"):
            path = os.path.join(pathDeviceTypeInstance, item)
            DataImport([path]).execute(graph, "deviceType")

    DataImport(["data/knowledgeBase/vul.txt", "data/knowledgeBase/vendor.txt"]).execute(graph, "vulnerability")
    DataImport(["data/knowledgeBase/done.txt"]).execute(graph, "deviceVendor")
    pathDitingInstance = "data/knowledgeBase/diting"
    for item in os.listdir(pathDitingInstance):
        if item.endswith(".json"):
            path = os.path.join(pathDitingInstance, item)
            DataImport([path, "data/knowledgeBase/vendor.txt"]).execute(graph, "diting_instance")


def knowledgeBaseFormatting(graph):
    vertices = []

    vertices.extend(DataImport(["data/knowledgeBase/vendor.txt"]).execute(graph, "vendor"))
    vertices.extend(DataImport(["data/knowledgeBase/protocol.txt"]).execute(graph, "protocol"))
    vertices.extend(DataImport(["data/knowledgeBase/done.txt"]).execute(graph, "deviceVendor"))
    vertices.extend(
        DataImport(["data/knowledgeBase/vul.txt", "data/knowledgeBase/vendor.txt"]).execute(graph, "vulnerability"))
    vertices.extend(DataImport(["data/knowledgeBase/Camera.json"]).execute(graph, "camera_instance"))

    pathZoomeyeInstance = "data/knowledgeBase/zoomeye"
    for item in os.listdir(pathZoomeyeInstance):
        if item.endswith(".json"):
            path = os.path.join(pathZoomeyeInstance, item)
            vertices.extend(DataImport([path, "data/knowledgeBase/vendor.txt"]).execute(graph, "zoomeye_instance"))

    pathDeviceTypeInstance = "data/knowledgeBase/deviceType"
    for item in os.listdir(pathDeviceTypeInstance):
        if item.endswith(".txt"):
            path = os.path.join(pathDeviceTypeInstance, item)
            vertices.extend(DataImport([path]).execute(graph, "deviceType"))

    vertices.extend(
        DataImport(["data/knowledgeBase/vul.txt", "data/knowledgeBase/vendor.txt"]).execute(graph, "vulnerability"))
    vertices.extend(DataImport(["data/knowledgeBase/done.txt"]).execute(graph, "deviceVendor"))
    pathDitingInstance = "data/knowledgeBase/diting"
    for item in os.listdir(pathDitingInstance):
        if item.endswith(".json"):
            path = os.path.join(pathDitingInstance, item)
            vertices.extend(DataImport([path, "data/knowledgeBase/vendor.txt"]).execute(graph, "diting_instance"))

    vertices = _remove_duplicate(vertices)
    types = ["protocol", "deviceType", "device", "instance", "vendor", "event", "vulnerability"]
    fileDic = {}
    for type in types:
        file = open("data/knowledgeBaseSQL/%s.txt" % type, "w")
        file.truncate()
        fileDic[type] = file

    for vertex in vertices:
        type = vertex.get('type', 'none')
        fileDic[type].write(__getRecord(vertex, type))


def __getRecord(vertex, type):
    if type not in JSON:
        return ""
    list = JSON[type]["properties"]
    s = ""
    for i in range(len(list)):
        s += str(vertex.get(list[i], "")).replace("\r\n", "///").replace("\n", "///")
        if i == len(list) - 1:
            s += "\n"
        else:
            s += "|"
    return s


def _remove_duplicate(dict_list):
    val_list = []
    unique_dict_list = []
    for i in range(len(dict_list)):
        if dict_list[i]['name'] not in val_list:
            val_list.append(dict_list[i]['name'])
            unique_dict_list.append(dict_list[i])
    return unique_dict_list


taskList = []
threadLock = threading.Lock()


class Import(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        global taskList
        while True:
            threadLock.acquire()
            if len(taskList) == 0:
                threadLock.release()
                return
            task = taskList.pop(0)
            threadLock.release()
            DataImport(task[0], self.server).execute(task[1], task[2], threadLock)


def execute():
    thread1 = Import("http://10.1.1.47:8182")
    thread2 = Import("http://10.1.1.48:8182")
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def main():
    # graph1Import("graph1")
    # graph2Import("graph2")
    # execute()

    # knowledgeBaseImport("knowledgeBase")
    knowledgeBaseFormatting("knowledgeBaseSQL")


if __name__ == '__main__':
    main()
