#!/usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import json
import sys


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


class knowledgeBase_FormattingProcess(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def vendor_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        lines = list(set(lines))

        for line in lines:
            line = line.strip().split('\t')
            name = line[0]
            country = ''
            url = ''
            if len(line) > 1:
                country = line[1]
            if len(line) > 2:
                url = line[2]

            # Add vertices
            vertices.append({'name': name, 'type': 'vendor', 'country': country, 'url': url})

        vertices = _remove_duplicate(vertices)
        return vertices

    def protocol_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        lines = list(set(lines))

        for line in lines:
            line = line.strip().split()
            name = line[0]

            # Add vertices
            vertices.append({'name': name, 'type': 'protocol'})

        vertices = _remove_duplicate(vertices)

        return vertices

    def zoomeye_instance_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r')
        fileB = codecs.open(self.file_path[1], 'r')  # vendor in fileB
        try:
            ins = json.load(file)
        except Exception as e:
            print(e)
        finally:
            file.close()
        try:
            linesB = fileB.readlines()
        except Exception as e:
            print(e)
        finally:
            fileB.close()

        # get vendor Name
        venName = []
        linesB = list(set(linesB))
        for line in linesB:
            line = line.strip().split(',')
            venName.append(line[0])

        # Add vertices
        protocol = ins[0]['protocol']
        vertices.append({'name': protocol, 'type': 'protocol'})
        ins.pop(0)

        for match in ins:
            city = match['geoinfo']['city']['names']['en']
            if city == None:
                city = "None"
            country = match['geoinfo']['country']['names']['en']
            if country == None:
                country = "None"
            continent = match['geoinfo']['continent']['names']['en']
            if continent == None:
                continent = "None"
            asn = match['geoinfo']['asn']
            lat = match['geoinfo']['location']['lat']
            lon = match['geoinfo']['location']['lon']
            ip = match['ip']
            hostname = match['portinfo']['hostname']
            service = match['portinfo']['service']
            os = match['portinfo']['os']
            app = match['portinfo']['app']
            extrainfo = match['portinfo']['extrainfo']
            version = match['portinfo']['version']
            device = match['portinfo']['device']
            port = match['portinfo']['port']
            banner = match['portinfo']['banner']
            timestamp = match['timestamp']

            # Add vertices
            ##modified##
            vertices.append(
                {'name': ip, 'type': 'instance', 'type_index': 'instance', 'ins_type': protocol, 'ip': ip, 'city': city,
                 'country': country, 'continent': continent, 'asn': asn, 'lat': lat, 'lon': lon, 'hostname': hostname,
                 'service': service, 'os': os, 'app': app, 'extrainfo': extrainfo, 'version': version, 'port': port,
                 'banner': banner, 'timestamp': timestamp})
            vertices.append({'name': protocol, 'type': 'protocol'})

        # Remove duplicated vertices
        vertices = _remove_duplicate(vertices)
        return vertices

    def diting_instance_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r')
        fileB = codecs.open(self.file_path[1], 'r')  # vendor in fileB
        try:
            ins = json.load(file)
        except Exception as e:
            print(e)
        finally:
            file.close()
        try:
            linesB = fileB.readlines()
        except Exception as e:
            print(e)
        finally:
            fileB.close()

        # get vendor Name
        venName = []
        linesB = list(set(linesB))
        for line in linesB:
            line = line.strip().split(',')
            venName.append(line[0])

        num = 0  # distinguish ip
        for match in ins:
            timestamp = match['timestamp']
            port = match['port']
            banner = match['Banner']
            protocol = (match['Service'].split('Service '))[1]
            if protocol == "S7":
                protocol = "Siemens S7"
            elif protocol == "fox":
                protocol = "Tridium Niagara Fox"
            elif protocol == "melsec-q":
                protocol = "MELSEC-Q"
            elif protocol == "modbus":
                protocol = "Modbus"
            elif protocol == "Redlion Crimson3":
                protocol = "Crimson V3"
            location = (match['Location'].split('Location '))[1]
            country = (location.split(' : '))[0]
            city = (location.split(' : '))[1]
            ip = match['ip'] + protocol + str(num)
            num = num + 1
            ##modified##
            rawIP = match['ip']
            lat = match['lat']
            lon = match['lon']
            port = match['port']

            # Add vertices
            vertices.append({'name': protocol, 'type': 'protocol'})
            ##modified##
            vertices.append(
                {'name': ip, 'type': 'instance', 'type_index': 'instance', 'ins_type': protocol, 'ip': rawIP,
                 'city': city, 'country': country, 'banner': banner, 'timestamp': timestamp, 'port': port, 'lat': lat,
                 'lon': lon})

        # Remove duplicated vertices
        vertices = _remove_duplicate(vertices)
        return vertices

    ##modified_add##
    def camera_instance_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r')
        try:
            ins = json.load(file)
        except Exception as e:
            print(e)
        finally:
            file.close()
        for match in ins:
            lat = match['lat']
            lon = match['lon']
            banner = match['banner']
            timestamp = match['timestamp']
            ip = match['ip']
            country = match['country']
            city = match['city']
            port = match['port']
            asn = match['asn']

            # Add vertices
            vertices.append(
                {'name': ip, 'type': 'instance', 'type_index': 'instance', 'ins_type': 'Camera', 'lat': lat, 'lon': lon,
                 'ip': ip, 'country': country, 'city': city, 'banner': banner, 'timestamp': timestamp, 'port': port,
                 'asn': asn})

        vertices = _remove_duplicate(vertices)
        return vertices

    def vulnerability_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r', encoding='utf-8')
        fileB = codecs.open(self.file_path[1], 'r', encoding='utf-8')  # vendor in fileB
        try:
            lines = file.readlines()
            linesB = fileB.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()
            fileB.close()

        # get vendor Name
        venName = []
        linesB = list(set(linesB))
        for line in linesB:
            line = line.strip().split(',')
            venName.append(line[0])

        # Remove duplicated lines
        lines = list(set(lines))

        for line in lines:
            line = line.strip().split('\t')
            if len(line) == 1:
                continue
            name = line[0]
            level = line[1]
            devices = line[2].strip().split('! !')
            description = line[3]
            url = line[4]
            mitigation = line[5]
            provider = line[6]
            timestamp = line[7]

            # Add vertices
            vertices.append(
                {'name': name, 'type': 'vulnerability', 'level': level, 'description': description, 'url': url,
                 'mitigation': mitigation, 'provider': provider, 'timestamp': timestamp})
            for device in devices:
                device = device.strip()
                if device == '(暂无)':
                    continue
                vertices.append({'name': device, 'type': 'device'})

        # Remove duplicated vertices
        vertices = _remove_duplicate(vertices)
        return vertices

    def deviceType_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        lines = list(set(lines))

        for line in lines:
            line = line.strip().split('\t')
            device = line[0]
            name = line[2]
            if name == "未归类":
                name = "others"
            # Add vertices
            vertices.append({'name': name, 'type': 'deviceType'})
            vertices.append({'name': device, 'type': 'device'})

        # Remove duplicated vertices
        vertices = _remove_duplicate(vertices)
        return vertices

    def deviceVendor_preprocess(self):
        vertices = []

        file = codecs.open(self.file_path[0], 'r')
        try:
            lines = file.readlines()
        except Exception as e:
            print(e)
        finally:
            file.close()

        lines = list(set(lines))

        for line in lines:
            line = line.strip().split('\t')
            if len(line) > 2:
                device = line[0]
                vendor = line[2]
            if device == '(暂无)':
                continue  #####mark
            # Add vertices
            vertices.append({'name': device, 'type': 'device'})
            vertices.append({'name': vendor, 'type': 'vendor'})

        # Remove duplicated vertices
        vertices = _remove_duplicate(vertices)
        return vertices

    ##########
    @classmethod
    def judgeVen(self, vpArr, str):
        for vp in vpArr:
            if vp in str:
                return vp
        return None


def main():
    test = knowledgeBase_DataPreProcess(
        ["data/knowledgeBase/diting/outIEC 60870-5-104.json", "data/knowledgeBase/vendor.txt"])
    vertices = test.diting_instance_preprocess()
    # test = knowledgeBase_DataPreProcess(["data/knowledgeBase/Camera.json"])
    # v,e = test.camera_instance_preprocess()
    print(vertices)


if __name__ == '__main__':
    main()
