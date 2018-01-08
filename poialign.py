#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import OsmData
import osmcmd

def getClosestPointOnWay(fpt,waypts):
	mi=None
	ml2=float('inf')
	mp=None
	# try segment endpoints
	for i,wpt in enumerate(waypts):
		v=wpt-fpt
		l2=v.x**2+v.y**2
		if l2<ml2:
			ml2=l2
			mp=wpt
			mi=(i,)
	# try points inside segments
	ml=math.sqrt(ml2)
	for i,wp1,wp2 in [(i,waypts[i],waypts[i+1]) for i in range(len(waypts)-1)]:
		fp1=fpt
		dwp=wp2-wp1
		fp2=fp1+osmcmd.Vector(-dwp.y,dwp.x).dir() # fake point to make perpendicular line
		l,s=osmcmd.shoot(fp1,fp2,wp1,wp2)
		if s<0 or s>1:
			continue
		if abs(l)<ml:
			ml=abs(l)
			mp=wp1+(wp2-wp1)*s
			mi=(i,i+1)
	return mp,mi

def main():
	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)
	if len(opdata.ways)<1:
		osmcmd.fail('ERROR: no way to align POIs')
	if len(opdata.ways)>1:
		osmcmd.fail('ERROR: too many way to align POIs')
	buildingWayId=next(iter(opdata.ways))
	buildingWay=data.ways[buildingWayId]
	buildingWayPoints=osmcmd.makePointsFromWay(buildingWay,data)

	def makeEntranceAndConnect(poiNodeId,entranceNodeId):
		entranceNode=data.nodes[entranceNodeId]
		if entranceNode[OsmData.TAG].get('entrance') is None:
			if entranceNode.get(OsmData.ACTION)!=OsmData.CREATE:
				entranceNode[OsmData.ACTION]=OsmData.MODIFY
			entranceNode[OsmData.TAG]['entrance']=poiNode[OsmData.TAG]['entrance']
		corridorWayId=data.addway()
		corridorWay=data.ways[corridorWayId]
		corridorWay[OsmData.REF]=[entranceNodeId,poiNodeId]
		corridorWay[OsmData.TAG]['highway']='corridor'

	for poiNodeId in opdata.nodes:
		poiNode=data.nodes[poiNodeId]
		fpt=osmcmd.makePointFromNode(poiNode)
		wpt,wpi=getClosestPointOnWay(fpt,buildingWayPoints)
		tpt=wpt+(fpt-wpt).dir()*osmcmd.Length(2,wpt)
		poiNode[OsmData.ACTION]=OsmData.MODIFY
		poiNode[OsmData.LON]=tpt.lon
		poiNode[OsmData.LAT]=tpt.lat
		if poiNode[OsmData.TAG].get('entrance') is not None:
			if len(wpi)==1:
				entranceNodeId=buildingWay[OsmData.REF][wpi[0]]
				makeEntranceAndConnect(poiNodeId,entranceNodeId)
			elif len(wpi)==2:
				entranceNodeId,_=osmcmd.makeNodeFromPoint(data,wpt)
				buildingWay[OsmData.ACTION]=OsmData.MODIFY
				buildingWay[OsmData.REF].insert(wpi[1],entranceNodeId)
				makeEntranceAndConnect(poiNodeId,entranceNodeId)
			del poiNode[OsmData.TAG]['entrance']
	data.write(sys.stdout)

if __name__=='__main__':
	main()
