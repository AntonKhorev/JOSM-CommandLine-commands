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
	pr=sys.argv[3]
	if '|' in pr:
		a,b=(float(t) for t in pr.split('|'))
		w1=b/(a+b)
		w2=a/(a+b)
	else:
		w2=float(pr)
		w1=1-w2

	pm=(
		p1[0]*w1+p2[0]*w2,
		p1[1]*w1+p2[1]*w2,
	)

	tData=OsmData.OsmData()
	addNode(tData,pm)

	tData.addcomment("Done.")
	tData.write(sys.stdout)

if __name__=='__main__':
	main()
