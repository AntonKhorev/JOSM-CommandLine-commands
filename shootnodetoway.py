#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd
import OsmData

def sntw(data,nodeid,wayid):
	node=data.nodes[nodeid]
	nodept=osmcmd.Point('latlon',node[OsmData.LAT],node[OsmData.LON])
	way=data.ways[wayid]
	waypts=[osmcmd.Point('latlon',waynode[OsmData.LAT],waynode[OsmData.LON]) for waynode in [
		data.nodes[id] for id in way[OsmData.REF]
	]]

	mi=None
	ml=float('inf')
	ms=float('inf')
	for i,wp1,wp2 in [(i,waypts[i],waypts[i+1]) for i in range(len(waypts)-1)]:
		np1=nodept
		dwp=wp2-wp1
		np2=np1+osmcmd.Vector(-dwp.y,dwp.x) # fake point to make perpendicular line
		l,s=osmcmd.solveLinEqns((
			(np2.x-np1.x,wp2.x-wp1.x,np1.x-wp1.x),
			(np2.y-np1.y,wp2.y-wp1.y,np1.y-wp1.y),
		))
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
	nodeid=next(iter(nodedata.nodes))
	data.mergedata(nodedata)
	waydata=osmcmd.readData()
	wayid=next(iter(waydata.ways))
	data.mergedata(waydata)
	id=sntw(data,nodeid,wayid)
	if id is None:
		resultdata=osmcmd.Data()
		resultdata.write('Impossible')
	else:
		data.addcomment('Done')
		data.write(sys.stdout)

if __name__=='__main__':
	main()
