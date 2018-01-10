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
		np2=np1+(wp2-wp1).rot90().dir() # fake point to make perpendicular line
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
	id,_=osmcmd.makeNodeFromPoint(data,wp1+(wp2-wp1)*ms)
	data.ways[wayid][OsmData.ACTION]=OsmData.MODIFY
	data.ways[wayid][OsmData.REF].insert(mi+1,id)
	return id

def swtw(data,wcid,wuid):
	wc=data.ways[wcid]
	wcpts=osmcmd.makePointsFromWay(wc,data)
	wu=data.ways[wuid]
	wupts=osmcmd.makePointsFromWay(wu,data)

	mi=None
	ml=float('inf')
	mf=None
	for f,pc1,pc2 in ((True,wcpts[1],wcpts[0]),(False,wcpts[-2],wcpts[-1])):
		for i,pu1,pu2 in ((i,wupts[i],wupts[i+1]) for i in range(len(wupts)-1)):
			if pc2==pu1 or pc2==pu2:
				continue
			l,s=osmcmd.shoot(pc1,pc2,pu1,pu2)
			if s<0 or s>1 or l<1:
				continue
			if l<ml:
				ml=l
				mi=i
				mf=f

	if mi is None:
		return None

	pc1,pc2 = (wcpts[1],wcpts[0]) if mf else (wcpts[-2],wcpts[-1])
	id,_=osmcmd.makeNodeFromPoint(data,pc1+(pc2-pc1)*ml)
	data.ways[wuid][OsmData.ACTION]=OsmData.MODIFY
	data.ways[wuid][OsmData.REF].insert(mi+1,id)
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
