#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd
import OsmData

def main():
	refdata=osmcmd.readData()
	wcdata=osmcmd.readData()
	wcid,wc=next(iter(wcdata.ways.items()))
	wcpts=[osmcmd.Point('latlon',node[OsmData.LAT],node[OsmData.LON]) for node in [
		refdata.nodes[id] for id in wc[OsmData.REF]
	]]
	wudata=osmcmd.readData()
	wuid,wu=next(iter(wudata.ways.items()))
	wupts=[osmcmd.Point('latlon',node[OsmData.LAT],node[OsmData.LON]) for node in [
		refdata.nodes[id] for id in wu[OsmData.REF]
	]]

	resultdata=osmcmd.Data()
	if wcid==wuid:
		resultdata.write('Same way')
		return

	mi=None
	ml=float('inf')
	mf=None
	for f,pc1,pc2 in ((True,wcpts[0],wcpts[1]),(False,wcpts[-1],wcpts[-2])):
		for i,pu1,pu2 in [(i,wupts[i],wupts[i+1]) for i in range(len(wupts)) if i<len(wupts)-1]:
			l,s=osmcmd.solveLinEqns((
				(pc2.x-pc1.x,pu2.x-pu1.x,pc1.x-pu1.x),
				(pc2.y-pc1.y,pu2.y-pu1.y,pc1.y-pu1.y),
			))
			if s<0 or s>1 or l<0:
				continue
			if l<ml:
				ml=l
				mi=i
				mf=f

	if mi is None:
		resultdata.write('Impossible')
		return

	#resultdata.write('Intersects after pt '+str(mi))
	pc1,pc2 = (wcpts[0],wcpts[1]) if mf else (wcpts[-1],wcpts[-2])
	pi=pc1+(pc1-pc2)*ml
	#resultdata.addNode(pi)
	#resultdata.write()
	id=wudata.addnode()
	wudata.nodes[id][OsmData.LON]=pi.lon
	wudata.nodes[id][OsmData.LAT]=pi.lat
	wudata.nodes[id][OsmData.TAG]={}
	wudata.ways[wuid][OsmData.ACTION]=OsmData.MODIFY
	wudata.ways[wuid][OsmData.REF].insert(mi+1,id)
	wudata.addcomment('Done')
	wudata.write(sys.stdout)

if __name__=='__main__':
	main()
