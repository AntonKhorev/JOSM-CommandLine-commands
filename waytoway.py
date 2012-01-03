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

	pc1=wcpts[0]
	pc2=wcpts[1]
	mi=None
	ml=float('inf')
	for i,pu1,pu2 in [(i,wupts[i],wupts[i+1]) for i in range(len(wupts)) if i<len(wupts)-1]:
		det =(pc2.x-pc1.x)*(pu2.y-pu1.y)-(pu2.x-pu1.x)*(pc2.y-pc1.y)
		detl=(pc1.x-pu1.x)*(pu2.y-pu1.y)-(pu2.x-pu1.x)*(pc1.y-pu1.y)
		dets=(pc2.x-pc1.x)*(pc1.y-pu1.y)-(pc1.x-pu1.x)*(pc2.y-pc1.y)
		l=detl/det
		s=dets/det
		if s<0 or s>1:
			continue
		if l<ml:
			ml=l
			mi=i

	td=osmcmd.Data()
	if mi is None:
		td.write('Impossible')
	else:
		#td.write('Intersects after pt '+str(mi))
		pi=pc1+(pc1-pc2)*ml
		td.addNode(pi)
		td.write()

if __name__=='__main__':
	main()
