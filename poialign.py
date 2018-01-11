#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import OsmData
import osmcmd

epsilon=1e-7
maxIterations=1000
delta=10/maxIterations

def shootPoint(fp1,wp1,wp2):
	fp2=fp1+(wp2-wp1).rot90().dir() # fake point to make perpendicular line
	return osmcmd.shoot(fp1,fp2,wp1,wp2)

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
	sides=[]
	ml=math.sqrt(ml2)
	for i,wp1,wp2 in [(i,waypts[i],waypts[i+1]) for i in range(len(waypts)-1)]:
		l,s=shootPoint(fpt,wp1,wp2)
		sides.append(math.copysign(1,l))
		if s<0 or s>1:
			continue
		if abs(l)<ml:
			ml=abs(l)
			mp=wp1+(wp2-wp1)*s
			mi=(i,i+1)
	return mp,mi,sides

def getPoiAndEntranceLocations(poiPoint,buildingWayPoints,offsetLength):
	entrancePoint,buildingWayIndices,initialSides=getClosestPointOnWay(poiPoint,buildingWayPoints)
	if offsetLength<(poiPoint-entrancePoint).length:
		# pull mode
		newPoiPoint=entrancePoint+(poiPoint-entrancePoint).dir(offsetLength)
		return newPoiPoint,entrancePoint,buildingWayIndices
	# push mode
	pusher0=None
	pusher1=None
	isClosedWay=buildingWayPoints[0]==buildingWayPoints[-1]
	p=poiPoint
	def pushByPoint(wp): # invalidates l1,s1, but it shouldn't affect the result
		return p+(p-wp).dir(offsetLength*delta)
	def pushBySegment(s,wp1,wp2,initialSide): # invalidates l1,s1, but it shouldn't affect the result
		nv=(wp2-wp1).rot90().dir(-initialSide*offsetLength*delta)
		return p+nv
	for nIterations in range(maxIterations):
		isModified=False
		def recordPush(pusher):
			nonlocal isModified,pusher0,pusher1
			isModified=True
			pusher0=pusher1
			pusher1=pusher
		if isClosedWay:
			l1,s1=shootPoint(p,buildingWayPoints[-2],buildingWayPoints[-1])
		else:
			l1,s1=shootPoint(p,buildingWayPoints[1],buildingWayPoints[0])
		for i,wp1,wp2 in [(i,buildingWayPoints[i],buildingWayPoints[i+1]) for i in range(len(buildingWayPoints)-1)]:
			l0,s0=l1,s1
			l1,s1=shootPoint(p,wp1,wp2)
			if s0>1 and s1<0 and (p-wp1).length<offsetLength-epsilon:
				p=pushByPoint(wp1)
				recordPush((i,))
			if 0<=s1<=1 and l1*initialSides[i]<offsetLength-epsilon:
				p=pushBySegment(s1,wp1,wp2,initialSides[i])
				recordPush((i,i+1))
		if not isClosedWay:
			l0,s0=l1,s1
			l1,s1=shootPoint(p,wp2,wp1)
			if s0>1 and s1<0 and (p-wp1).length<offsetLength-epsilon:
				p=pushByPoint(wp1)
				recordPush((i,))
		if not isModified:
			break
	if pusher1 is None:
		return p,None,None
	elif len(pusher1)==1:
		return p,buildingWayPoints[pusher1[0]],pusher1
	elif len(pusher1)==2 and (pusher0 is None or len(pusher0)==1 or pusher0==pusher1):
		wp1=buildingWayPoints[pusher1[0]]
		wp2=buildingWayPoints[pusher1[1]]
		l,s=shootPoint(p,wp1,wp2)
		ep=wp1+(wp2-wp1)*s
		return p,ep,pusher1
	elif len(pusher1)==2 and len(pusher0)==2:
		if pusher1[1]==pusher0[0]:
			pusher0,pusher1=pusher1,pusher0
		if pusher0[1]==pusher1[0]:
			return p,buildingWayPoints[pusher1[0]],(pusher1[0],)
		else:
			return p,None,None
	else:
		return p,None,None

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
		poiNode=data.nodes[poiNodeId]
		poiPoint=osmcmd.makePointFromNode(poiNode)
		offsetLength=poiPoint.lengthFromMeters(2)
		buildingWayPoints=osmcmd.makePointsFromWay(buildingWay,data) # get points again in case the way was altered
		buildingWayNodeIds=buildingWay[OsmData.REF]
		isBuildingWayClosed=buildingWayNodeIds[0]==buildingWayNodeIds[-1]
		def getBuildingSegmentsAroundIndex(j):
			if 0<j<len(buildingWayNodeIds)-1:
				return buildingWayPoints[j-1:j+2]
			elif isBuildingWayClosed:
				return [buildingWayPoints[-2],buildingWayPoints[0],buildingWayPoints[1]]
			elif j==0:
				return buildingWayPoints[:2]
			else:
				return buildingWayPoints[-2:]
		connectedToBuildingIndices=set()
		def getPossibleBuildingConnections():
			for cwid in connectorWayIds:
				connectorWayNodeIds=data.ways[cwid][OsmData.REF]
				for i,cwid in enumerate(connectorWayNodeIds):
					if cwid==poiNodeId:
						for j,bwid in enumerate(buildingWayNodeIds):
							if (not isBuildingWayClosed or j>0) and (
								(i>0 and bwid==connectorWayNodeIds[i-1]) or
								(i<len(connectorWayNodeIds)-1 and bwid==connectorWayNodeIds[i+1])
							):
								connectedToBuildingIndices.add(j)
		getPossibleBuildingConnections()
		if len(connectedToBuildingIndices)==1:
			for j in connectedToBuildingIndices:
				connectionPoint=osmcmd.makePointFromNode(data.nodes[buildingWayNodeIds[j]])
				poiPoint=connectionPoint+(poiPoint-connectionPoint).dir(offsetLength*delta)
				buildingWayPoints=getBuildingSegmentsAroundIndex(j)
		newPoiPoint,entrancePoint,buildingWayIndices=getPoiAndEntranceLocations(poiPoint,buildingWayPoints,offsetLength)
		poiNode[OsmData.ACTION]=OsmData.MODIFY
		poiNode[OsmData.LON]=newPoiPoint.lon
		poiNode[OsmData.LAT]=newPoiPoint.lat
		if poiNode[OsmData.TAG].get('entrance') is not None and entrancePoint is not None:
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
