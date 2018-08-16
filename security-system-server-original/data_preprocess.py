#!/usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import hashlib
import re
import socket
import struct
import time


class Case_1_DataPreProcess(object):
    def __init__(self, file_path):
        self.file_path = file_path.decode('utf-8')

    def flow_preprocess(self):
        vertexes = []
        edges = []

        file = codecs.open(self.file_path, 'r', encoding='utf-8')
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

            # Add vertexes
            vertexes.append({'name': src_ip, 'type': 'ip', 'province': src_province, 'country': src_country})
            vertexes.append({'name': dst_ip, 'type': 'ip', 'province': dst_province, 'country': dst_country})

            # Format time
            timeArray = time.strptime(record_time, "%Y/%m/%dT%H:%M:%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            # Add edges
            hash_val = hashlib.md5(''.join(line)).hexdigest()
            edges.append({'type': 'access', 'src': src_ip, 'dst': dst_ip, 'src_port': src_port, 'dst_port': dst_port,
                          'time': format_time, 'pkg_num': pkg_num, 'bytes': bytes, 'protocol': protocol,
                          'TCP_flag': TCP_flag, 'hash': hash_val})

        # Remove duplicated vertexes
        vertexes = list(dict(t) for t in set([tuple(d.items()) for d in vertexes]))
        return vertexes, edges

    def jsp_preprocess(self):
        vertexes = []
        edges = []

        file = codecs.open(self.file_path, 'r', encoding='utf-8')
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
            vertexes.append({'name': src_ip, 'type': 'ip'})
            vertexes.append({'name': dst_ip, 'type': 'ip'})

            # Add domain
            pattern_domain = re.compile(r'(Host:)(.*?)(\\)')
            try:
                domain = pattern_domain.search(return_val).group(2).strip()
            except Exception as e:
                print(e)
            vertexes.append({'name': domain, 'type': 'domain'})

            # Add url
            pattern_dir = re.compile(r'(\/)(.*?)(HTTP)')
            try:
                url = domain + '/' + pattern_dir.search(resp).group(2).strip()
            except Exception as e:
                print(e)
            vertexes.append({'name': url, 'type': 'url'})

            timeArray = time.strptime(record_time, "%Y%m%d%H%M%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            # Add edges
            hash_val = hashlib.md5(''.join(line)).hexdigest()
            edges.append({'type': 'attack', 'src': src_ip, 'dst': dst_ip, 'src_port': src_port, 'dst_port': dst_port,
                          'time': format_time, 'in_out_port': in_out_port, 'evt_name': evt_name,
                          'device_name': device_name, 'return_val': return_val, 'hash': hash_val})
            edges.append(
                {'type': 'ip2domain', 'src': dst_ip, 'dst': domain, 'hash': hashlib.md5(dst_ip + domain).hexdigest()})
            edges.append({'type': 'url2domain', 'src': url, 'dst': domain, 'time': format_time,
                          'hash': hashlib.md5(url + domain).hexdigest()})
            edges.append({'type': 'ip2url', 'src': src_ip, 'dst': url, 'time': format_time,
                          'hash': hashlib.md5(src_ip + url).hexdigest()})

        # Remove duplicated vertexes
        vertexes = list(dict(t) for t in set([tuple(d.items()) for d in vertexes]))
        return vertexes, edges


class Case_2_DataPreProcess(object):
    def __init__(self, file_path):
        self.file_path = file_path.decode('utf-8')

    def ip2long(self, ip):
        # Convert an IP string to long
        packedIP = socket.inet_aton(ip)
        return struct.unpack("!L", packedIP)[0]

    def long2ip(self, ip_long):
        return socket.inet_ntoa(struct.pack('!L', ip_long))

    def depmt_preprocess(self):
        vertexes = []
        edges = []

        file = codecs.open(self.file_path, 'r', encoding='utf-8')
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

            vertexes.append({'name': department, 'type': 'department', 'info': info})

            ip_area = ip_range.split(',')
            ip_end = self.ip2long(ip_area[1])
            ip_start = self.ip2long(ip_area[0])

            for i in range(ip_end - ip_start + 1):
                ip_tmp = self.long2ip(ip_start + i)
                vertexes.append({'name': ip_tmp, 'type': 'ip', 'province': province, 'country': country})

                hash_val = hashlib.md5(department + ip_tmp).hexdigest()
                edges.append({'type': 'ip2dep', 'src': ip_tmp, 'dst': department, 'hash': hash_val})

        # Remove duplicated vertexes
        vertexes = list(dict(t) for t in set([tuple(d.items()) for d in vertexes]))
        return vertexes, edges

    def download_preprocess(self):
        vertexes = []
        edges = []

        file = codecs.open(self.file_path, 'r', encoding='utf-8')
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

            vertexes.append({'name': control_ip, 'type': 'ip'})
            vertexes.append({'name': dep_ip, 'type': 'ip'})
            vertexes.append({'name': file_md5, 'type': 'file', 'info': file_md5})
            vertexes.append({'name': url, 'type': 'url', 'info': url})

            timeArray = time.strptime(record_time, "%Y-%m-%d-%H:%M:%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            edges.append(
                {'type': 'ip2file', 'src': dep_ip, 'dst': file_md5, 'time': format_time, 'download_from': control_ip,
                 'download_url': url, 'hash': hash_val})
            edges.append(
                {'type': 'file2url', 'src': file_md5, 'dst': url, 'hash': hashlib.md5(file_md5 + url).hexdigest()})
            edges.append(
                {'type': 'url2ip', 'src': url, 'dst': control_ip, 'hash': hashlib.md5(url + control_ip).hexdigest()})

        # Remove duplicated vertexes
        vertexes = list(dict(t) for t in set([tuple(d.items()) for d in vertexes]))
        return vertexes, edges

    def dns_preprocess(self):
        vertexes = []
        edges = []

        file = codecs.open(self.file_path, 'r', encoding='utf-8')
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

            vertexes.append({'name': resolution_ip, 'type': 'ip'})
            vertexes.append({'name': src_ip, 'type': 'ip'})
            vertexes.append({'name': req_domain, 'type': 'domain'})

            timeArray = time.strptime(record_time, "%Y%m%d%H%M%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            hash_val = hashlib.md5(''.join(line[0:13])).hexdigest()
            edges.append({'type': 'dnsrequest', 'src': src_ip, 'dst': req_domain, 'dns_server': dns_server_ip,
                          'protocol': protocol, 'req_domain': req_domain, 'req_type': req_type,
                          'req_counts': req_counts, 'direction': direction, 'resp_flag': resp_flag,
                          'resp_val': resp_val, 'rr_req_type': rr_req_type, 'resolution_ip': resolution_ip, 'ttl': ttl,
                          'time': format_time, 'sampling_rate': sampling_rate, 'hash': hash_val})
            edges.append({'type': 'domain2ip', 'src': req_domain, 'dst': resolution_ip})

        # Remove duplicated vertexes
        vertexes = list(dict(t) for t in set([tuple(d.items()) for d in vertexes]))
        return vertexes, edges

    def flow_preprocess(self):
        vertexes = []
        edges = []

        file = codecs.open(self.file_path, 'r', encoding='utf-8')
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

            vertexes.append({'name': src_ip, 'type': 'ip', 'location': src_province, 'country': src_country})
            vertexes.append({'name': dst_ip, 'type': 'ip', 'location': dst_province, 'country': dst_country})

            timeArray = time.strptime(record_time, "%Y%m%d%H%M%S")
            format_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)

            edges.append({'type': 'access', 'src': src_ip, 'dst': dst_ip, 'src_port': src_port, 'dst_port': dst_port,
                          'pkg_num': pkg_num, 'bytes': bytes, 'time': format_time, 'TCP_flag': TCP_flag,
                          'protocol': protocol, 'hash': hash_val})

        # Remove duplicated vertexes
        vertexes = list(dict(t) for t in set([tuple(d.items()) for d in vertexes]))
        return vertexes, edges


def main():
    #    test = Case_1_DataPreProcess('F:\\FLOW-20160513-dip.txt')
    #    vertexes, edges = test.flow_preprocess()
    #   print  edges

    test = Case_2_DataPreProcess(r'F:\\flow财务部-flow-36.56.42.48-20160201-20160208.txt')
    vertexes, edges = test.flow_preprocess()
    print("%s %s" % (len(vertexes), len(edges)))


if __name__ == '__main__':
    main()
