#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd
import OsmData

def sntw(data,nodeid,wayid):
	node=data.nodes[nodeid]
	nodept=osmcmd.Point.fromNode(node)
	way=data.ways[wayid]
	wayChain=osmcmd.Chain.fromWay(way,data)

	mi=None
	ml=float('inf')
	ms=float('inf')
	for i,waySegment in enumerate(wayChain.segments):
		l,s=waySegment.project(nodept)
		if s<0 or s>1:
			continue
		if abs(l)<abs(ml):
			mi=i
			ml=l
			ms=s

	if mi is None:
		return None

	id,_=wayChain.segments[mi].displace(ms).makeNode(data)
	way[OsmData.ACTION]=OsmData.MODIFY
	way[OsmData.REF].insert(mi+1,id)
	return id

def swtw(data,wcid,wuid):
	wc=data.ways[wcid]
	wcChain=osmcmd.Chain.fromWay(wc,data)
	wu=data.ways[wuid]
	wuChain=osmcmd.Chain.fromWay(wu,data)

	mi=None
	ml=float('inf')
	mf=None
	for f,pcSegment in ((True,wcChain.segments[0].rev()),(False,wcChain.segments[-1])):
		for i,puSegment in enumerate(wuChain.segments):
			if pcSegment.p2==puSegment.p1 or pcSegment.p2==puSegment.p2:
				continue
			l,s=pcSegment.intersect(puSegment)
			if s<0 or s>1 or l<1:
				continue
			if l<ml:
				ml=l
				mi=i
				mf=f

	if mi is None:
		return None

	pcSegment = wcChain.segments[0].rev() if mf else wcChain.segments[-1]
	id,_=pcSegment.displace(ml).makeNode(data)
	wu[OsmData.ACTION]=OsmData.MODIFY
	wu[OsmData.REF].insert(mi+1,id)
	return id

def main():
	data=osmcmd.readData()
	fromdata=osmcmd.readData()
	data.mergedata(fromdata)
	todata=osmcmd.readData()
	data.mergedata(todata)
	toid=next(iter(todata.ways))

	nn=0
	nns=0
	for fromid in fromdata.nodes:
		id=sntw(data,fromid,toid)
		if id is None:
			nns+=1
		else:
			nn+=1

	nw=0
	nws=0
	for fromid in fromdata.ways:
		if fromid==toid:
			nws+=1
			continue
		id=swtw(data,fromid,toid)
		if id is None:
			nws+=1
		else:
			nw+=1

	if nw>0 or nn>0:
		data.addcomment(str(nn)+' nodes shot, '+str(nns)+' nodes skipped, '+str(nw)+' ways shot, '+str(nws)+' ways skipped')
		data.write(sys.stdout)
	else:
		osmcmd.fail('WARNING: no nodes/ways shot')

if __name__=='__main__':
	main()
