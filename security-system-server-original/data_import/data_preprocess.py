#!/usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import hashlib
import re
import socket
import struct
import sys
import time


def _remove_duplicate(dict_list):
    val_list = []
    unique_dict_list = []
    for i in range(len(dict_list)):
        if dict_list[i]['name'] not in val_list:
            val_list.append(dict_list[i]['name'])
            unique_dict_list.append(dict_list[i])
    return unique_dict_list


def index(srcV, dstV):
    return srcV + "-****-" + dstV


class graph1_DataPreProcess(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def flow_preprocess(self):
        vertices = []
        edges = []

        file = codecs.open(self.file_path, 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()
        # Remove title line
        lines.pop(0)
        # Remove duplicated lines
        lines = list(set(lines))

        for line in lines:
            line = line.strip().split()
            src_ip = line[0]
            dst_ip = line[1]
            pkg_num = line[2]
            bytes = line[3]
            record_time = line[4]
            src_port = line[5]
            dst_port = line[6]
            TCP_flag = line[7]
            protocol = line[8]
            src_province = line[9]
            dst_province = line[10]
            src_country = line[11]
            dst_country = line[12]

            # Add vertices
            vertices.append({'name': src_ip, 'type': 'ip', 'province': src_province, 'country': src_country})
            vertices.append({'name': dst_ip, 'type': 'ip', 'province': dst_province, 'country': dst_country})

            # Format time
            timeArray = time.strptime(record_time, "%Y/%m/%dT%H:%M:%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            # Add edges
            hash_val = hashlib.md5(''.join(line)).hexdigest()
            edges.append(
                {'type': 'access', 'INDEX': index(src_ip, dst_ip), 'srcV': src_ip, 'dstV': dst_ip, 'srcPort': src_port,
                 'dstPort': dst_port, 'time': format_time, 'packages': pkg_num, 'bytes': bytes, 'transProto': protocol,
                 'tcpFlag': TCP_flag, 'hash': hash_val})

        # Remove duplicated vertices and edges

        vertices = _remove_duplicate(vertices)
        edges = list(dict(t) for t in set([tuple(d.items()) for d in edges]))
        return vertices, edges

    def jsp_preprocess(self):
        vertices = []
        edges = []

        file = codecs.open(self.file_path, 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        # Remove title line
        lines.pop(0)
        # Remove duplicated lines
        lines = list(set(lines))

        for line in lines:
            line = line.strip().split('\t')
            in_out_port = line[0]
            evt_name = line[1]
            src_ip = line[2]
            dst_ip = line[3]
            src_port = line[4]
            dst_port = line[5]
            record_time = line[6]
            device_name = line[7]
            return_val = line[8]

            # Add ip
            vertices.append({'name': src_ip, 'type': 'ip'})
            vertices.append({'name': dst_ip, 'type': 'ip'})

            # Add domain
            pattern_domain = re.compile(r'(Host:)(.*?)(\\)')
            try:
                domain = pattern_domain.search(return_val).group(2).strip()
            except Exception as e:
                print(e)
            vertices.append({'name': domain, 'type': 'domain'})

            # Add url
            pattern_dir = re.compile(r'(\/)(.*?)(HTTP)')
            try:
                url = domain + '/' + pattern_dir.search(return_val).group(2).strip()
            except Exception as e:
                print(e)
            vertices.append({'name': url, 'type': 'url'})

            timeArray = time.strptime(record_time, "%Y%m%d%H%M%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            # Add edges
            hash_val = hashlib.md5(''.join(line)).hexdigest()
            edges.append(
                {'type': 'attack', 'INDEX': index(src_ip, dst_ip), 'srcV': src_ip, 'dstV': dst_ip, 'srcPort': src_port,
                 'dstPort': dst_port, 'time': format_time, 'in_out_port': in_out_port, 'event': evt_name,
                 'device': device_name, 'returnValue': return_val, 'hash': hash_val})
            edges.append({'type': 'ip2domain', 'INDEX': index(dst_ip, domain), 'srcV': dst_ip, 'dstV': domain,
                          'hash': hashlib.md5(dst_ip + domain).hexdigest()})
            edges.append(
                {'type': 'domain2url', 'INDEX': index(domain, url), 'srcV': domain, 'dstV': url, 'time': format_time,
                 'hash': hashlib.md5(domain + url).hexdigest()})
            edges.append(
                {'type': 'ip2url', 'INDEX': index(src_ip, url), 'srcV': src_ip, 'dstV': url, 'time': format_time,
                 'hash': hashlib.md5(src_ip + url).hexdigest()})

        # Remove duplicated vertices and edges
        vertices = _remove_duplicate(vertices)
        edges = list(dict(t) for t in set([tuple(d.items()) for d in edges]))
        return vertices, edges


class graph2_DataPreProcess(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def ip2long(self, ip):
        # Convert an IP string to long
        packedIP = socket.inet_aton(ip)
        return struct.unpack("!L", packedIP)[0]

    def long2ip(self, ip_long):
        return socket.inet_ntoa(struct.pack('!L', ip_long))

    def depmt_preprocess(self):
        vertices = []
        edges = []

        file = codecs.open(self.file_path, 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        # Remove title line
        lines.pop(0)
        # Remove duplicated lines
        lines = list(set(lines))

        for line in lines:
            line = line.strip().split()
            department = line[0]
            info = line[0]
            ip_range = line[1]
            country = line[2]
            province = line[3]

            vertices.append({'name': department, 'type': 'department', 'info': info})

            ip_area = ip_range.split(',')
            ip_end = self.ip2long(ip_area[1])
            ip_start = self.ip2long(ip_area[0])

            for i in range(ip_end - ip_start + 1):
                ip_tmp = self.long2ip(ip_start + i)
                vertices.append({'name': ip_tmp, 'type': 'ip', 'province': province, 'country': country})

                hash_val = hashlib.md5(ip_tmp + department).hexdigest()
                edges.append({'type': 'ip2dep', 'INDEX': index(ip_tmp, department), 'srcV': ip_tmp, 'dstV': department,
                              'hash': hash_val})

        # Remove duplicated vertices and edges
        vertices = _remove_duplicate(vertices)
        edges = list(dict(t) for t in set([tuple(d.items()) for d in edges]))
        return vertices, edges

    def download_preprocess(self):
        vertices = []
        edges = []

        file = codecs.open(self.file_path, 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        # Remove title line
        lines.pop(0)
        # Remove duplicated lines
        lines = list(set(lines))

        for line in lines:
            line = line.strip().split()
            record_time = line[0]
            control_ip = line[1]
            dep_ip = line[2]
            url = line[3]
            file_md5 = line[4]
            hash_val = hashlib.md5(''.join(line[0:4])).hexdigest()

            vertices.append({'name': control_ip, 'type': 'ip'})
            vertices.append({'name': dep_ip, 'type': 'ip'})
            vertices.append({'name': file_md5, 'type': 'file', 'info': file_md5})
            vertices.append({'name': url, 'type': 'url', 'info': url})

            timeArray = time.strptime(record_time, "%Y-%m-%d-%H:%M:%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            edges.append({'type': 'ip2file', 'INDEX': index(dep_ip, file_md5), 'srcV': dep_ip, 'dstV': file_md5,
                          'time': format_time, 'DSI': control_ip, 'DSU': url, 'hash': hash_val})
            edges.append({'type': 'url2file', 'INDEX': index(url, file_md5), 'srcV': url, 'dstV': file_md5,
                          'hash': hashlib.md5(url + file_md5).hexdigest()})
            edges.append({'type': 'ip2url', 'INDEX': index(control_ip, url), 'srcV': control_ip, 'dstV': url,
                          'hash': hashlib.md5(control_ip + url).hexdigest()})

        # Remove duplicated vertices and edges
        vertices = _remove_duplicate(vertices)
        edges = list(dict(t) for t in set([tuple(d.items()) for d in edges]))
        return vertices, edges

    def dns_preprocess(self):
        vertices = []
        edges = []

        file = codecs.open(self.file_path, 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        # Remove title line
        lines.pop(0)
        # Remove duplicated lines
        lines = list(set(lines))

        for line in lines:
            line = line.strip().split()
            src_ip = line[0]
            dns_server_ip = line[1]
            protocol = line[2]
            req_domain = line[3]
            req_type = line[4]
            req_counts = line[5]
            direction = line[6]
            resp_flag = line[7]
            resp_val = line[8]
            rr_req_type = line[9]
            resolution_ip = line[10]
            ttl = line[11]
            record_time = line[12]
            sampling_rate = line[13]

            vertices.append({'name': resolution_ip, 'type': 'ip'})
            vertices.append({'name': src_ip, 'type': 'ip'})
            vertices.append({'name': req_domain, 'type': 'domain'})

            timeArray = time.strptime(record_time, "%Y%m%d%H%M%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            hash_val = hashlib.md5(''.join(line[0:13])).hexdigest()
            edges.append({'type': 'DNS', 'INDEX': index(src_ip, req_domain), 'srcV': src_ip, 'dstV': req_domain,
                          'DNSServer': dns_server_ip, 'transProto': protocol, 'reqDomain': req_domain,
                          'reqType': req_type, 'reqCount': req_counts, 'direct': direction, 'respFlag': resp_flag,
                          'respVal': resp_val, 'RPReqType': rr_req_type, 'RSIP': resolution_ip, 'TTL': ttl,
                          'time': format_time, 'SR': sampling_rate, 'hash': hash_val})
            edges.append({'type': 'ip2domain', 'INDEX': index(resolution_ip, req_domain), 'srcV': resolution_ip,
                          'dstV': req_domain})

        # Remove duplicated vertices and edges
        vertices = _remove_duplicate(vertices)
        edges = list(dict(t) for t in set([tuple(d.items()) for d in edges]))
        return vertices, edges

    def flow_preprocess(self):
        vertices = []
        edges = []

        file = codecs.open(self.file_path, 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        # Remove title line
        lines.pop(0)
        # Remove duplicated lines
        lines = list(set(lines))

        for line in lines:
            line = line.strip().split()
            record_time = line[0]
            src_ip = line[1]
            dst_ip = line[2]
            src_port = line[3]
            dst_port = line[4]
            protocol = line[5]
            TCP_flag = line[6]
            pkg_num = line[7]
            bytes = line[8]
            src_country = line[9]
            src_province = line[10]
            dst_country = line[11]
            dst_province = line[12]
            hash_val = hashlib.md5(''.join(line)).hexdigest()

            vertices.append({'name': src_ip, 'type': 'ip', 'province': src_province, 'country': src_country})
            vertices.append({'name': dst_ip, 'type': 'ip', 'province': dst_province, 'country': dst_country})

            timeArray = time.strptime(record_time, "%Y%m%d%H%M%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            edges.append(
                {'type': 'access', 'INDEX': index(src_ip, dst_ip), 'srcV': src_ip, 'dstV': dst_ip, 'srcPort': src_port,
                 'dstPort': dst_port, 'packages': pkg_num, 'bytes': bytes, 'time': format_time, 'tcpFlag': TCP_flag,
                 'transProto': protocol, 'hash': hash_val})

        # Remove duplicated vertices and edges
        vertices = _remove_duplicate(vertices)
        edges = list(dict(t) for t in set([tuple(d.items()) for d in edges]))
        return vertices, edges


def main():
    test = case1_DataPreProcess(r'C:\Users\ye\Desktop\data_import\data_import\data\flow.txt')
    vertices, edges = test.flow_preprocess()
    for v in vertices:
        print(v['name'])


if __name__ == '__main__':
    main()
