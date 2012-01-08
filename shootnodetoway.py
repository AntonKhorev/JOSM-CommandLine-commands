#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd
import OsmData

def main():
	refdata=osmcmd.readData()
	ncdata=osmcmd.readData()
	ncid,nc=next(iter(ncdata.nodes.items()))
	ncpt=osmcmd.Point('latlon',nc[OsmData.LAT],nc[OsmData.LON])
	wudata=osmcmd.readData()
	wuid,wu=next(iter(wudata.ways.items()))
	wupts=[osmcmd.Point('latlon',node[OsmData.LAT],node[OsmData.LON]) for node in [
		refdata.nodes[id] for id in wu[OsmData.REF]
	]]

	resultdata=osmcmd.Data()

	mi=None
	ml=float('inf')
	ms=float('inf')
	for i,pu1,pu2 in [(i,wupts[i],wupts[i+1]) for i in range(len(wupts)) if i<len(wupts)-1]:
		pc1=ncpt
		dpu=pu2-pu1
		pc2=pc1+osmcmd.Vector(-dpu.y,dpu.x) # fake point to make perpendicular line
		l,s=osmcmd.solveLinEqns((
			(pc2.x-pc1.x,pu2.x-pu1.x,pc1.x-pu1.x),
			(pc2.y-pc1.y,pu2.y-pu1.y,pc1.y-pu1.y),
		))
		if s<0 or s>1:
			continue
		if abs(l)<abs(ml):
			mi=i
			ml=l
			ms=s

	if mi is None:
		resultdata.write('Impossible')
		return

	#resultdata.write('Intersects after pt '+str(mi))
	pu1,pu2=wupts[mi],wupts[mi+1]
	pi=pu1+(pu2-pu1)*ms
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
