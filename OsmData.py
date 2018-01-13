#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       OsmData.py
#       
#       Data processing routines for CommandLine plugin
#       
#       Copyright 2010-2011 Hind <foxhind@gmail.com>
#       modified by OverQuantum:
#       2014-12-12 Deleting section reversed - relations 1st, then ways and nodes (to not break data consistency inside command stack)
#       2014-12-13 Fix to 4 spaces indentation; added this header
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.        See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import xml.sax
import xml.sax.saxutils
import copy

def quoteattr(attr):
    return xml.sax.saxutils.quoteattr(str(attr))

LON = 1
LAT = 2
REF = 3
TAG = 4
ACTION = 5
VERSION = 6
USER = 7
UID = 8
CHANGESET = 9
CREATE = 0
MODIFY = 1
DELETE = 2
NODES = 0
WAYS = 1
RELATIONS = 2

class OsmData(xml.sax.ContentHandler):
    def __init__(self):
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.comments = []
        self.bbox = [0, 0, 0, 0] # minlon, minlat, maxlon, maxlat
        self.currnodeid = -1
        self.currwayid = -1
        self.currrelationid = -1
        self.currentObj = None
        self.currentId = None
    def addnode(self, Id=0):
        if Id == 0:
            while self.nodes.get(self.currnodeid) != None:
                self.currnodeid -= 1
            self.nodes[self.currnodeid] = {LON: 0, LAT: 0, ACTION: CREATE, TAG: {}}
            return self.currnodeid
        else:
            self.nodes[Id] = {ACTION: MODIFY}
            return Id
    def addway(self, Id=0):
        if Id == 0:
            while self.ways.get(self.currwayid) != None:
                self.currwayid -= 1
            self.ways[self.currwayid] = {ACTION: CREATE, TAG: {}, REF: []}
            return self.currwayid
        else:
            self.ways[Id] = {ACTION: MODIFY}
            return Id
    def mergedata(self, other):
        self.nodes.update(copy.deepcopy(other.nodes))
        self.ways.update(copy.deepcopy(other.ways))
        self.relations.update(copy.deepcopy(other.relations))
    def addcomment(self, text):
        self.comments += [text]
    def read(self, sourceStream):
        line = ''
        iparser = xml.sax.make_parser()
        iparser.setContentHandler(self)
        #f = open("sad.osm", "a")
        while line.find('</osm>') == -1:
            line = sourceStream.readline()
            iparser.feed(line)
            #f.write(line)
        #f.close()
    def write(self, targetStream):
        targetStream.write("<osm version=\"0.6\">\n")
        
        # Creating
        for node in self.nodes.items():
            if node[1].get(ACTION) != CREATE:
                continue
            targetStream.write(self.xmlnode(node))
        for way in self.ways.items():
            if way[1].get(ACTION) != CREATE:
                continue
            targetStream.write(self.xmlway(way))
        for relation in self.relations.items():
            if relation[1].get(ACTION) != CREATE:
                continue
            targetStream.write(self.xmlrelation(relation))
            
        # Modifying
        for node in self.nodes.items():
            if node[1].get(ACTION) != MODIFY:
                continue
            targetStream.write(self.xmlnode(node))
        for way in self.ways.items():
            if way[1].get(ACTION) != MODIFY:
                continue
            targetStream.write(self.xmlway(way))
        for relation in self.relations.items():
            if relation[1].get(ACTION) != MODIFY:
                continue
            targetStream.write(self.xmlrelation(relation))
        
        # Deleting
        for relation in self.relations.items():
            if relation[1].get(ACTION) != DELETE:
                continue
            targetStream.write(self.xmlrelation(relation))
        for way in self.ways.items():
            if way[1].get(ACTION) != DELETE:
                continue
            targetStream.write(self.xmlway(way))
        for node in self.nodes.items():
            if node[1].get(ACTION) != DELETE:
                continue
            targetStream.write(self.xmlnode(node))
        for text in self.comments:
            targetStream.write("<!--" + text + "-->\n")
        targetStream.write("</osm>")
    def xmlnode(self, node):
        string = ("<node id=" + quoteattr(node[0]) + " ");
        tags = {}
        for attr in node[1].items():
            if attr[0] == ACTION:
                if attr[1] == MODIFY:
                    string += ("action='modify' ");
                elif attr[1] == DELETE:
                    string += ("action='delete' ");
            elif attr[0] == VERSION:
                string += ("version=" + quoteattr(attr[1]) + " ")
            elif attr[0] == CHANGESET:
                string += ("changeset=" + quoteattr(attr[1]) + " ")
            elif attr[0] == UID:
                string += ("uid=" + quoteattr(attr[1]) + " ")
            elif attr[0] == LAT:
                string += ("lat=" + quoteattr(attr[1]) + " ")
            elif attr[0] == LON:
                string += ("lon=" + quoteattr(attr[1]) + " ")
            elif attr[0] == USER:
                string += ("user=" + quoteattr(attr[1]) + " ")
            elif attr[0] == "timestamp" or attr[0] == "visible":
                string += (attr[0] + "=" + quoteattr(attr[1]) + " ")
        if len(node[1][TAG]) > 0:
            string += (">\n")
            for tag in node[1][TAG].items():
                string += ("<tag k=" + quoteattr(tag[0]) + " v=" + quoteattr(tag[1]) + " />\n")
            string += ("</node>\n")
        else:
            string += ("/>\n")
        return string
    def xmlway(self, way):
        string = ("<way id=" + quoteattr(way[0]) + " ");
        tags = {}
        for attr in way[1].items():
            if attr[0] == ACTION:
                if attr[1] == MODIFY:
                    string += ("action='modify' ");
                elif attr[1] == DELETE:
                    string += ("action='delete' ");
            elif attr[0] == VERSION:
                string += ("version=" + quoteattr(attr[1]) + " ")
            elif attr[0] == CHANGESET:
                string += ("changeset=" + quoteattr(attr[1]) + " ")
            elif attr[0] == UID:
                string += ("uid=" + quoteattr(attr[1]) + " ")
            elif attr[0] == USER:
                string += ("user=" + quoteattr(attr[1]) + " ")
            elif attr[0] == "timestamp" or attr[0] == "visible":
                string += (attr[0] + "=" + quoteattr(attr[1]) + " ")
        string += (">\n")
        for ref in way[1][REF]:
            string += ("<nd ref=" + quoteattr(ref) + " />\n")
        for tag in way[1][TAG].items():
            string += ("<tag k=" + quoteattr(tag[0]) + " v=" + quoteattr(tag[1]) + " />\n")
        string += ("</way>\n")
        return string
    def xmlrelation(self, relation):
        string = ("<relation id=" + quoteattr(relation[0]) + " ");
        tags = {}
        for attr in relation[1].items():
            if attr[0] == ACTION:
                if attr[1] == MODIFY:
                    string += ("action='modify' ");
                elif attr[1] == DELETE:
                    string += ("action='delete' ");
            elif attr[0] == VERSION:
                string += ("version=" + quoteattr(attr[1]) + " ")
            elif attr[0] == CHANGESET:
                string += ("changeset=" + quoteattr(attr[1]) + " ")
            elif attr[0] == UID:
                string += ("uid=" + quoteattr(attr[1]) + " ")
            elif attr[0] == USER:
                string += ("user=" + quoteattr(attr[1]) + " ")
            elif attr[0] == "timestamp" or attr[0] == "visible":
                string += (attr[0] + "=" + quoteattr(attr[1]) + " ")
        string += (">\n")
        for ref in relation[1][REF][NODES]:
            string += ("<member type='node' ref=" + quoteattr(ref[0]) + " role=" + quoteattr(ref[1]) + " />\n")
        for ref in relation[1][REF][WAYS]:
            string += ("<member type='way' ref=" + quoteattr(ref[0]) + " role=" + quoteattr(ref[1]) + " />\n")
        for ref in relation[1][REF][RELATIONS]:
            string += ("<member type='relation' ref=" + quoteattr(ref[0]) + " role=" + quoteattr(ref[1]) + " />\n")
        for tag in relation[1][TAG].items():
            string += ("<tag k=" + quoteattr(tag[0]) + " v=" + quoteattr(tag[1]) + " />\n")
        string += ("</relation>\n")
        return string
    def startElement(self, tag, attributes):
        if tag == "node":
            self.currentObj = {}
            for attr in attributes.items():
                if attr[0] == "id":
                    self.currentId = int(attr[1])
                elif attr[0] == "version":
                    self.currentObj[VERSION] = int(attr[1])
                elif attr[0] == "changeset":
                    self.currentObj[CHANGESET] = int(attr[1])
                elif attr[0] == "uid":
                    self.currentObj[UID] = int(attr[1])
                elif attr[0] == "lat":
                    self.currentObj[LAT] = float(attr[1])
                    if self.currentObj[LAT] < self.bbox[1] or self.bbox[1] == 0:
                        self.bbox[1] = self.currentObj[LAT]
                    if self.currentObj[LAT] > self.bbox[3] or self.bbox[3] == 0:
                        self.bbox[3] = self.currentObj[LAT]
                elif attr[0] == "lon":
                    self.currentObj[LON] = float(attr[1])
                    if self.currentObj[LON] < self.bbox[0] or self.bbox[0] == 0:
                        self.bbox[0] = self.currentObj[LON]
                    if self.currentObj[LON] > self.bbox[2] or self.bbox[2] == 0:
                        self.bbox[2] = self.currentObj[LON]
                elif attr[0] == "user":
                    self.currentObj[USER] = attr[1]
            self.currentObj[TAG] = {}
        elif tag == "way":
            self.currentObj = {}
            for attr in attributes.items():
                if attr[0] == "id":
                    self.currentId = int(attr[1])
                elif attr[0] == "version":
                    self.currentObj[VERSION] = int(attr[1])
                elif attr[0] == "changeset":
                    self.currentObj[CHANGESET] = int(attr[1])
                elif attr[0] == "uid":
                    self.currentObj[UID] = int(attr[1])
                elif attr[0] == "user":
                    self.currentObj[USER] = attr[1]
            self.currentObj[TAG] = {}
            self.currentObj[REF] = []
        elif tag == "relation":
            self.currentObj = {}
            for attr in attributes.items():
                if attr[0] == "id":
                    self.currentId = int(attr[1])
                elif attr[0] == "version":
                    self.currentObj[VERSION] = int(attr[1])
                elif attr[0] == "changeset":
                    self.currentObj[CHANGESET] = int(attr[1])
                elif attr[0] == "uid":
                    self.currentObj[UID] = int(attr[1])
                elif attr[0] == "user":
                    self.currentObj[USER] = attr[1]
            self.currentObj[TAG] = {}
            self.currentObj[REF] = [[], [], []] # [Nodes, Ways, Relations]
        elif tag == "tag":
            self.currentObj[TAG][attributes.get("k")] = attributes.get("v")
        elif tag == "nd":
            for attr in attributes.items():
                if attr[0] == "ref":
                    self.currentObj[REF].append(int(attr[1]))
        elif tag == "member":
            mtype = attributes.get("type")
            if mtype == "node":
                self.currentObj[REF][NODES].append((int(attributes.get("ref")), attributes.get("role")))
            elif mtype == "way":
                self.currentObj[REF][WAYS].append((int(attributes.get("ref")), attributes.get("role")))
            elif mtype == "relation":
                self.currentObj[REF][RELATIONS].append((int(attributes.get("ref")), attributes.get("role")))
    def endElement(self, tag):
        if self.currentId != None:
            if tag == "node":
                self.nodes[self.currentId] = self.currentObj
            elif tag == "way":
                self.ways[self.currentId] = self.currentObj
            elif tag == "relation":
                self.relations[self.currentId] = self.currentObj

class Map():
    def __init__(self):
        self.number = 0
        self.omap = {}
    def __getitem__(self, oldkey):
        newkey = self.omap.get(oldkey)
        if newkey == None:
            self.number -= 1
            newkey = self.number
            self.omap[oldkey] = newkey
        return newkey
