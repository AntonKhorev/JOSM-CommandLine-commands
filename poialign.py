#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import OsmData
import osmcmd

epsilon=1e-7
maxIterations=1000
delta=10/maxIterations

def getClosestPointOnChain(fpt,chain):
	mi=None
	ml2=float('inf')
	mp=None
	# try segment endpoints
	for i,wpt in enumerate(chain.points):
		v=wpt-fpt
		l2=v.x**2+v.y**2
		if l2<ml2:
			ml2=l2
			mp=wpt
			mi=(i,)
	# try points inside segments
	ml=math.sqrt(ml2)
	for i,seg in enumerate(chain.segments):
		l,s=seg.project(fpt)
		if s<0 or s>1:
			continue
		if abs(l)<ml:
			ml=abs(l)
			mp=seg.displace(s)
			mi=(i,i+1)
	return mp,mi

def getPoiAndEntranceLocations(poiPoint,buildingChain,offsetLength):
	entrancePoint,buildingChainIndices=getClosestPointOnChain(poiPoint,buildingChain)
	if offsetLength<(poiPoint-entrancePoint).length:
		# pull mode
		newPoiPoint=entrancePoint+(poiPoint-entrancePoint).dir(offsetLength)
		return newPoiPoint,entrancePoint,buildingChainIndices
	# push mode
	pusher0=None
	pusher1=None
	p=poiPoint
	def pushByPoint(wp): # invalidates l1,s1, but it shouldn't affect the result
		return p+(p-wp).dir(offsetLength*delta)
	def pushBySegment(l,seg): # invalidates l1,s1, but it shouldn't affect the result
		nv=((seg.p1-seg.p2).rot90()*l).dir(offsetLength*delta)
		return p+nv
	for nIterations in range(maxIterations):
		isModified=False
		def recordPush(pusher):
			nonlocal isModified,pusher0,pusher1
			isModified=True
			pusher0=pusher1
			pusher1=pusher
		if buildingChain.isClosed:
			l1,s1=buildingChain.segments[-1].project(p)
		else:
			l1,s1=buildingChain.segments[0].rev().project(p)
		for i,seg in enumerate(buildingChain.segments):
			l0,s0=l1,s1
			l1,s1=seg.project(p)
			if s0>1 and s1<0 and (p-seg.p1).length<offsetLength-epsilon:
				p=pushByPoint(seg.p1)
				recordPush((i,))
			if 0<=s1<=1 and abs(l1)<offsetLength-epsilon:
				p=pushBySegment(l1,seg)
				recordPush((i,i+1))
		if not buildingChain.isClosed:
			l0,s0=l1,s1
			l1,s1=seg.rev().project(p)
			if s0>1 and s1<0 and (p-seg.p1).length<offsetLength-epsilon:
				p=pushByPoint(seg.p1)
				recordPush((i,))
		if not isModified:
			break
	if pusher1 is None:
		return p,None,None
	elif len(pusher1)==1:
		return p,buildingChain.points[pusher1[0]],pusher1
	elif len(pusher1)==2 and (pusher0 is None or len(pusher0)==1 or pusher0==pusher1):
		wp1=buildingChain.points[pusher1[0]]
		wp2=buildingChain.points[pusher1[1]]
		l,s=osmcmd.Segment(wp1,wp2).project(p)
		ep=wp1+(wp2-wp1)*s
		return p,ep,pusher1
	elif len(pusher1)==2 and len(pusher0)==2:
		if pusher1[1]==pusher0[0]:
			pusher0,pusher1=pusher1,pusher0
		if pusher0[1]==pusher1[0]:
			return p,buildingChain.points[pusher1[0]],(pusher1[0],)
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
		poiPoint=osmcmd.Point.fromNode(poiNode)
		offsetLength=poiPoint.lengthFromMeters(2)
		buildingChain=osmcmd.Chain.fromWay(buildingWay,data) # get points again in case the way was altered
		buildingWayNodeIds=buildingWay[OsmData.REF]
		isBuildingWayClosed=buildingWayNodeIds[0]==buildingWayNodeIds[-1]
		def getBuildingChainAroundIndex(j):
			pts=[]
			if 0<j<len(buildingWayNodeIds)-1:
				pts=buildingChain.points[j-1:j+2]
			elif isBuildingWayClosed:
				pts=[buildingChain.points[-2],buildingChain.points[0],buildingChain.points[1]]
			elif j==0:
				pts=buildingChain.points[:2]
			else:
				pts=buildingChain.points[-2:]
			return osmcmd.Chain(pts)
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
		if len(connectedToBuildingIndices)==1: # if poi is connected to the building, look only at segments adjacent to connection point
			for j in connectedToBuildingIndices:
				connectionPoint=osmcmd.Point.fromNode(data.nodes[buildingWayNodeIds[j]])
				poiPoint=connectionPoint+(poiPoint-connectionPoint).dir(offsetLength*delta)
				buildingChain=getBuildingChainAroundIndex(j)
		newPoiPoint,entrancePoint,buildingWayIndices=getPoiAndEntranceLocations(poiPoint,buildingChain,offsetLength)
		newPoiPoint.setNode(poiNode)
		if poiNode[OsmData.TAG].get('entrance') is not None and entrancePoint is not None:
			if len(buildingWayIndices)==1:
				entranceNodeId=buildingWay[OsmData.REF][buildingWayIndices[0]]
				makeEntranceAndConnect(poiNodeId,entranceNodeId)
			elif len(buildingWayIndices)==2:
				entranceNodeId,_=entrancePoint.makeNode(data)
				buildingWay[OsmData.ACTION]=OsmData.MODIFY
				buildingWay[OsmData.REF].insert(buildingWayIndices[1],entranceNodeId)
				makeEntranceAndConnect(poiNodeId,entranceNodeId)
			del poiNode[OsmData.TAG]['entrance']
	data.write(sys.stdout)

if __name__=='__main__':
	main()
