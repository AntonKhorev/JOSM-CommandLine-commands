#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import projections
import OsmData

def readPoint(n):
	t=sys.argv[n].split(',')
	return projections.from4326((float(t[0]),float(t[1])),"EPSG:3857")

def addNode(data,point):
	p=projections.to4326(point,"EPSG:3857")
	id=data.addnode()
	data.nodes[id][OsmData.LON]=p[0]
	data.nodes[id][OsmData.LAT]=p[1]
	data.nodes[id][OsmData.TAG]={}

def main():
	if len(sys.argv)!=4:
		return 0

	p1=readPoint(1)
	p2=readPoint(2)

	pm=(
		(p1[0]+p2[0])/2,
		(p1[1]+p2[1])/2,
	)

	tData=OsmData.OsmData()
	addNode(tData,pm)

	tData.addcomment("Done.")
	tData.write(sys.stdout)

if __name__=='__main__':
	main()
