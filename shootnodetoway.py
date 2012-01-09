#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd
import OsmData

def sntw():
	data=osmcmd.readData()
	ncdata=osmcmd.readData()
	ncid=next(iter(ncdata.nodes))
	data.mergedata(ncdata)
	wudata=osmcmd.readData()
	wuid=next(iter(wudata.ways))
	data.mergedata(wudata)

	nc=data.nodes[ncid]
	ncpt=osmcmd.Point('latlon',nc[OsmData.LAT],nc[OsmData.LON])
	wu=data.ways[wuid]
	wupts=[osmcmd.Point('latlon',node[OsmData.LAT],node[OsmData.LON]) for node in [
		data.nodes[id] for id in wu[OsmData.REF]
	]]

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
		raise Exception('Impossible')

	pu1,pu2=wupts[mi],wupts[mi+1]
	pi=pu1+(pu2-pu1)*ms
	id=data.addnode()
	data.nodes[id][OsmData.LON]=pi.lon
	data.nodes[id][OsmData.LAT]=pi.lat
	data.nodes[id][OsmData.TAG]={}
	data.ways[wuid][OsmData.ACTION]=OsmData.MODIFY
	data.ways[wuid][OsmData.REF].insert(mi+1,id)
	return data,ncid,id

def main():
	try:
		data,id1,id2=sntw()
		data.addcomment('Done')
		data.write(sys.stdout)
	except:
		resultdata=osmcmd.Data()
		resultdata.write('Impossible')

if __name__=='__main__':
	main()
