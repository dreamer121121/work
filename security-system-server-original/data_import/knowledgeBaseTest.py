#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import os
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

JSON = json.load(file("knowledgeBase.json"))["vertices"]


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
        file = open("data/knowledgeBaseSQL/%s.csv" % type, "w")
        file.truncate()
        fileDic[type] = [file, False]

    for vertex in vertices:
        type = vertex.get('type', 'none')
        if fileDic[type][1] == True:
            fileDic[type][0].write("\n")
        else:
            fileDic[type][1] = True
        fileDic[type][0].write(__getRecord(vertex, type))

    for type in types:
        fileDic[type][0].close()


def __getRecord(vertex, type):
    if type not in JSON:
        return ""
    list = JSON[type]["properties"]
    s = ""
    for i in range(len(list)):
        s += str(vertex.get(list[i], "")).replace("|", " ").replace("\r\n", "///").replace("\n", "///")
        if i != len(list) - 1:
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


def main():
    knowledgeBaseFormatting("knowledgeBaseSQL")


if __name__ == '__main__':
    main()
