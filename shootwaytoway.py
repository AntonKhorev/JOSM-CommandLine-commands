#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd
import OsmData

def swtw(data,wcid,wuid):
	wc=data.ways[wcid]
	wcpts=osmcmd.makePointsFromWay(wc,data)
	wu=data.ways[wuid]
	wupts=osmcmd.makePointsFromWay(wu,data)

	mi=None
	ml=float('inf')
	mf=None
	for f,pc1,pc2 in ((True,wcpts[0],wcpts[1]),(False,wcpts[-1],wcpts[-2])):
		for i,pu1,pu2 in ((i,wupts[i],wupts[i+1]) for i in range(len(wupts)-1)):
			l,s=osmcmd.shoot(pc1,pc2,pu1,pu2)
			if s<0 or s>1 or l<0:
				continue
			if l<ml:
				ml=l
				mi=i
				mf=f

	if mi is None:
		return None

	pc1,pc2 = (wcpts[0],wcpts[1]) if mf else (wcpts[-1],wcpts[-2])
	pi=pc1+(pc1-pc2)*ml
	id=data.addnode()
	data.nodes[id][OsmData.LON]=pi.lon
	data.nodes[id][OsmData.LAT]=pi.lat
	data.nodes[id][OsmData.TAG]={}
	data.ways[wuid][OsmData.ACTION]=OsmData.MODIFY
	data.ways[wuid][OsmData.REF].insert(mi+1,id)
	return id

def main():
	data=osmcmd.readData()
	wfdata=osmcmd.readData()
	data.mergedata(wfdata)
	wtdata=osmcmd.readData()
	data.mergedata(wtdata)
	wtid=next(iter(wtdata.ways))

	n=0
	ns=0
	for wfid in wfdata.ways:
		if wfid==wtid:
			ns+=1
			continue
		id=swtw(data,wfid,wtid)
		if id is None:
			ns+=1
		else:
			n+=1

	if n>0:
		data.addcomment(str(n)+' ways shot, '+str(ns)+' ways skipped')
		data.write(sys.stdout)
	else:
		resultdata=osmcmd.Data()
		resultdata.write('WARNING: no ways shot')

if __name__=='__main__':
	main()
