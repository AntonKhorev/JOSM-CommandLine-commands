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

def getPoiAndEntranceLocations(poiPoint,buildingWayPoints,offsetLength):
	entrancePoint,buildingWayIndices=getClosestPointOnWay(poiPoint,buildingWayPoints)
	newPoiPoint=entrancePoint+(poiPoint-entrancePoint).dir()*offsetLength
	return newPoiPoint,entrancePoint,buildingWayIndices

def main():
	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)
	buildingWayId=None
	connectorWayIds=[]
	for wid in opdata.ways:
		way=opdata.ways[wid]
		if way[OsmData.TAG].get('highway') is None:
			if buildingWayId is None:
				buildingWayId=wid
			else:
				osmcmd.fail('ERROR: too many building ways')
		else:
			connectorWayIds.append(wid)
	if buildingWayId is None:
		osmcmd.fail('ERROR: no building ways')
	buildingWay=data.ways[buildingWayId]

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
		buildingWayPoints=osmcmd.makePointsFromWay(buildingWay,data) # get points again in case the way was altered
		poiNode=data.nodes[poiNodeId]
		poiPoint=osmcmd.makePointFromNode(poiNode)
		newPoiPoint,entrancePoint,buildingWayIndices=getPoiAndEntranceLocations(poiPoint,buildingWayPoints,osmcmd.Length(2,poiPoint))
		poiNode[OsmData.ACTION]=OsmData.MODIFY
		poiNode[OsmData.LON]=newPoiPoint.lon
		poiNode[OsmData.LAT]=newPoiPoint.lat
		if poiNode[OsmData.TAG].get('entrance') is not None:
			if len(buildingWayIndices)==1:
				entranceNodeId=buildingWay[OsmData.REF][buildingWayIndices[0]]
				makeEntranceAndConnect(poiNodeId,entranceNodeId)
			elif len(buildingWayIndices)==2:
				entranceNodeId,_=osmcmd.makeNodeFromPoint(data,entrancePoint)
				buildingWay[OsmData.ACTION]=OsmData.MODIFY
				buildingWay[OsmData.REF].insert(buildingWayIndices[1],entranceNodeId)
				makeEntranceAndConnect(poiNodeId,entranceNodeId)
			del poiNode[OsmData.TAG]['entrance']
	data.write(sys.stdout)

if __name__=='__main__':
	main()
