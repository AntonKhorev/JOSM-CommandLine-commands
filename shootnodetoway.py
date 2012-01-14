#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd
import OsmData

def sntw(data,nodeid,wayid):
	node=data.nodes[nodeid]
	nodept=osmcmd.makePointFromNode(node)
	way=data.ways[wayid]
	waypts=osmcmd.makePointsFromWay(way,data)

	mi=None
	ml=float('inf')
	ms=float('inf')
	for i,wp1,wp2 in [(i,waypts[i],waypts[i+1]) for i in range(len(waypts)-1)]:
		np1=nodept
		dwp=wp2-wp1
		np2=np1+osmcmd.Vector(-dwp.y,dwp.x) # fake point to make perpendicular line
		l,s=osmcmd.shoot(np1,np2,wp1,wp2)
		if s<0 or s>1:
			continue
		if abs(l)<abs(ml):
			mi=i
			ml=l
			ms=s

	if mi is None:
		return None

	wp1,wp2=waypts[mi],waypts[mi+1]
	pi=wp1+(wp2-wp1)*ms
	id=data.addnode()
	data.nodes[id][OsmData.LON]=pi.lon
	data.nodes[id][OsmData.LAT]=pi.lat
	data.nodes[id][OsmData.TAG]={}
	data.ways[wayid][OsmData.ACTION]=OsmData.MODIFY
	data.ways[wayid][OsmData.REF].insert(mi+1,id)
	return id

def main():
	data=osmcmd.readData()
	nodedata=osmcmd.readData()
	data.mergedata(nodedata)
	waydata=osmcmd.readData()
	wayid=next(iter(waydata.ways))
	data.mergedata(waydata)
	n=0
	ns=0
	for nodeid in nodedata.nodes:
		id=sntw(data,nodeid,wayid)
		if id is None:
			ns+=1
		else:
			n+=1

	if n>0:
		data.addcomment(str(n)+' nodes shot, '+str(ns)+' nodes skipped')
		data.write(sys.stdout)
	else:
		resultdata=osmcmd.Data()
		resultdata.write('WARNING: no nodes shot')

if __name__=='__main__':
	main()
