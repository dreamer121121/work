#!/usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import time

import gremlinrestclient


class DataImport(object):
    def __init__(self, graph, file_path):
        self.graph = graph
        self.file_path = file_path

    def flow_import(self):
        vertices = {'ip': {}, 'domain': {}, 'url': {}}
        edges = []

        try:
            file = codecs.open(self.file_path, 'r', encoding='utf-8')
        except Exception as e:
            print(e)

        lines = file.readlines()
        lines.pop(0)
        start = time.time()
        count = 0
        for line in lines:
            line = line.strip().split()

            source = {"label": "IP_SCHEME_TRACE", "IP_ADD_SCHEME_TRACE": line[2]}
            count += 1
            self.graph.create(source)
            tmp = time.time()
            print("Inserting: " + line[2])
            print("Runtime: " + str(tmp - start))
            print("Number: " + str(count))


def main():
    url = "http://10.1.1.48:8182"
    graph = gremlinrestclient.TinkerGraph(url)

    DataImport(graph, "E:\source_data\offline_attk_qihu_acc_edu").flow_import()
    end = time.time()
    print("Total time: " + str(end - start))


if __name__ == '__main__':
    main()
