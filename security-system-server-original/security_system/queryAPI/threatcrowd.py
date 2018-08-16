import json
import requests


def RqIP(ip):
    txt = requests.get("https://www.threatcrowd.org/searchApi/v2/ip/report/", {"ip": ip})
    result = json.loads(txt.text)
    return result


def RqDomain(domain):
    txt = requests.get("http://www.threatcrowd.org/searchApi/v2/domain/report/", {"domain": domain})
    result = json.loads(txt.text)
    return result


def RqEmail(email):
    txt = requests.get("https://www.threatcrowd.org/searchApi/v2/email/report/", {"email": email})
    result = json.loads(txt.text)
    return result


def RqMD5(hash):
    txt = requests.get("https://www.threatcrowd.org/searchApi/v2/email/report/", {"resource": hash})
    result = json.loads(txt.text)
    return result


def add(source, type, nodes, edges, rootid, id):
    if source == "-":
        return id
    node = {}
    edge = {}
    redge = {}
    nodeid = id
    for node1 in nodes:
        if node1["name"] == source:
            nodeid = node1["id"]
    if nodeid == id:
        node["id"] = nodeid
        node["name"] = source
        node["type"] = type
        nodes.append(node)
    edge["srcID"] = rootid
    edge["dstID"] = nodeid
    for edge1 in edges:
        if ((edge1["srcID"] == nodeid) & (edge1["dstID"] == rootid)):
            return id + 1
    edges.append(edge)
    id += 1
    return id


def Threat(type, obj):
    result = {}
    nodes = []
    edges = []
    id = 2
    results = {}
    # type = 1
    hashes = {}
    emails = {}
    resolutions = {}
    node1 = {}
    # obj = "188.40.75.132"
    if type == '1':
        result = RqIP(obj)
        node1["type"] = "ip"
    elif type == '2':
        result = RqDomain(obj)
        node1["type"] = "domain"
    elif type == '3':
        result = RqEmail(obj)
        node1["type"] = "email"
    else:
        result = RqMD5(obj)
        node1["type"] = "hash"
    node1["id"] = 1
    node1["name"] = obj
    nodes.append(node1)
    isgood = result["response_code"]
    print(isgood)
    if "resolutions" in result:
        resolutions = result["resolutions"]
    if "hashes" in result:
        hashes = result["hashes"]
    if "emails" in result:
        emails = result["emails"]
    for hsh in hashes:
        id = add(hsh, "hash", nodes, edges, 1, id)
    for em in emails:
        id = add(em, "email", nodes, edges, 1, id)
    print(id)
    for resolution in resolutions:
        if "ip_address" in resolution:
            result = RqIP(resolution["ip_address"])
            rootid = id
            id = add(resolution["ip_address"], "ip", nodes, edges, 1, id)
            if "resolutions" in result:
                resolutions = result["resolutions"]
            if "hashes" in result:
                hashes = result["hashes"]
            if "emails" in result:
                emails = result["emails"]
            for hsh in hashes:
                id = add(hsh, "hash", nodes, edges, rootid, id)
            for em in emails:
                id = add(em, "email", nodes, edges, rootid, id)
            for resolution in resolutions:
                if "ip_address" in resolution:
                    name = resolution["ip_address"]
                    type = "ip"
                else:
                    name = resolution["domain"]
                    type = "domain"
                id = add(name, type, nodes, edges, rootid, id)
        else:
            result = RqDomain(resolution["domain"])
            rootid = id
            id = add(resolution["domain"], "domain", nodes, edges, 1, id)
            if "resolutions" in result:
                resolutions = result["resolutions"]
            if "hashes" in result:
                hashes = result["hashes"]
            if "emails" in result:
                emails = result["emails"]
            for hsh in hashes:
                id = add(hsh, "hash", nodes, edges, rootid, id)
            for em in emails:
                id = add(em, "email", nodes, edges, rootid, id)
            for resolution in resolutions:
                if "ip_address" in resolution:
                    name = resolution["ip_address"]
                    type = "ip"
                else:
                    name = resolution["domain"]
                    type = "domain"
                id = add(name, type, nodes, edges, rootid, id)
    results["isgood"] = isgood
    results["nodes"] = nodes
    results["edges"] = edges
    return results
