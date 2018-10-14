#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)
	cornerNids=set(opdata.nodes)
	for wid in opdata.ways:
		way=opdata.ways[wid]
		wayNids=way[OsmData.REF]
		cornerSegmentIds=[]
		for nid1,nid2 in ((wayNids[i],wayNids[i+1]) for i in range(len(wayNids)-1)):
			if nid1 not in cornerNids and nid2 in cornerNids:
				cornerSegmentIds.append((nid1,nid2))
			if nid1 in cornerNids and nid2 not in cornerNids:
				cornerSegmentIds.append((nid2,nid1))
		if len(cornerSegmentIds)<1:
			data.addcomment('Could not find enough corner segments for way #'+str(wid))
			break
		if len(cornerSegmentIds)>2:
			data.addcomment('Found too many corner segments for way #'+str(wid))
			break
		segment1=osmcmd.Segment.fromNodes(
			data.nodes[cornerSegmentIds[0][0]],
			data.nodes[cornerSegmentIds[0][1]]
		)
		segment2=osmcmd.Segment.fromNodes(
			data.nodes[cornerSegmentIds[1][0]],
			data.nodes[cornerSegmentIds[1][1]]
		)
		x,y=segment1.intersect(segment2)
		cornerPoint=segment1.displace(x)
		cornerNid,cornerNode=cornerPoint.makeNode(data)
		cornerWid=data.addway()
		cornerWay=data.ways[cornerWid]
		cornerWay[OsmData.REF]=[cornerSegmentIds[0][1],cornerNid,cornerSegmentIds[1][1]]
		data.addcomment('Restored corner for way #'+str(wid))
	data.write(sys.stdout)

if __name__=='__main__':
	main()
