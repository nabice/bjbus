#!/usr/bin/env python
#coding:utf8
import base64
import hashlib
import rc4
import urllib2
import xml.etree.ElementTree as ET
import re
import sys
import json
import os
import socket
from os.path import dirname, abspath, join

ETC_PATH=join(dirname(dirname(abspath(__file__))), "etc")
XML_PATH=join(ETC_PATH, "lines")
def decrypt(encrypt_text, key):
    if encrypt_text == None:
        return ""
    encrypt_text = base64.b64decode(encrypt_text)
    key = hashlib.md5('aibang{:s}'.format(key)).hexdigest()
    return rc4.rc4(encrypt_text, key)

def save_bus_info(lineid, businfo):
    root = ET.fromstring(businfo)
    for el in root.findall(".//"):
        if el.tag in ["shotname", "linename", "coord", "name", "no", "lon", "lat"]:
            el.text = decrypt(el.text, lineid).decode("utf8")
    with open(join(XML_PATH, lineid+".xml"), "w") as f:
        f.write(ET.tostring(root))
def get_lines_info():
    opener = urllib2.build_opener()
    opener.addheaders = [("cid", "1")]
    index_file = join(ETC_PATH, "busindex.xml")
    newindex = opener.open("http://mc.aibang.com/aiguang/bjgj.c?m=checkUpdate&version=1").read()
    if os.path.exists(index_file):
        oldmd5 = hashlib.md5(open(join(ETC_PATH, "busindex.xml"), 'rb').read()).hexdigest()
        if oldmd5 == hashlib.md5(newindex).hexdigest():
            print "Already updated"
            sys.exit(0)

    root = ET.fromstring(newindex)
    lines = root.findall(".//lines/line")
        
    for line in lines:
        lineid =  line.find("id").text
        version = line.find("version").text
        old_line_file = join(XML_PATH, lineid+".xml")
        if os.path.exists(old_line_file):
            old_version = ET.fromstring(open(old_line_file).read()).find("busline/version").text
            if version == old_version:
                continue
        businfo = opener.open("http://mc.aibang.com/aiguang/bjgj.c?m=update&id="+lineid).read()
        print "Saving", lineid
        save_bus_info(lineid, businfo)

    f = open(index_file, 'w')
    f.write(newindex)
    f.close()

    print_all_lines(False)

def usage():
    print "Usage: "+os.path.basename(__file__)+" -ul"
    print "       "+os.path.basename(__file__)+" LINEID"
    print "Beijing Real Bus!"
    print ""
    print "  -h           print this help"
    print "  -u           update bus list"
    print "  -l           list all lines"
    print ""
    print "Report bugs to <nabice@163.com>"
    sys.exit(0)

def print_all_lines(display=True):
    xmls = os.listdir(XML_PATH)
    f = open(join(ETC_PATH, "busallline"), "w")
    for xml in xmls:
        xmlroot = ET.parse(join(XML_PATH, xml))
        status = xmlroot.find("busline/status").text
        if status == "1":
            continue
        line = os.path.splitext(xml)[0] + " " + xmlroot.find("busline/linename").text.encode("utf8")
        time = xmlroot.find("busline/time").text
        if time:
            line += " " + time.encode("utf8")
        f.write(line + "\n")
        if display:
            print line
    f.close()
    
def real_bus(lineid):
    socket.setdefaulttimeout(3)
    for i in range(2):
        real_infos = False
        try:
            real_infos = json.loads(urllib2.urlopen("http://bjgj.aibang.com:8899/bus.php?id="+lineid+"&no=3&datatype=json&encrypt=1").read())["root"]["data"]["bus"]
        except urllib2.URLError as err:
            if isinstance(err.reason, socket.timeout):
                continue
        break
    if real_infos == False:
        sys.exit(1)
    buses = []
    for info in real_infos:
        buses.append({
            "name": decrypt(info["ns"], info["gt"]),
            "num": decrypt(info["nsn"], info["gt"]),
            "nsd": info["nsd"]
        })
    buses.sort(key=lambda bus:(int(bus["num"]), -int(bus["nsd"])))
    for bus in buses:
        print "{:s},{:s}".format(bus["name"], bus["nsd"])
if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '-h':
        usage()
    elif sys.argv[1] == '-l':
        print_all_lines()
        sys.exit(0)
    elif sys.argv[1] == '-u':
        get_lines_info()
        sys.exit(0)
    else:
        real_bus(sys.argv[1])
