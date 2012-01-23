#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	def enumWayPtPairs(way):
		refs=way[OsmData.REF]
		return ((i,osmcmd.makePointFromNode(data.nodes[refs[i]]),osmcmd.makePointFromNode(data.nodes[refs[i+1]])) for i in range(len(refs)-1))
	def segmentsCross(pa1,pa2,pb1,pb2):
		a,b=osmcmd.shoot(pa1,pa2,pb1,pb2)
		return a>0 and a<1 and b>0 and b<1
	def waysCross(crid,whid):
		return any(
			segmentsCross(crpt1,crpt2,whpt1,whpt2)
			for cri,crpt1,crpt2 in enumWayPtPairs(data.ways[crid])
			for whi,whpt1,whpt2 in enumWayPtPairs(data.ways[whid])
		)
	def makeCrossing(crid,whids):
		return 0,0

	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)

	candidates=[
		crid for crid in opdata.ways if all(
			waysCross(crid,whid) for whid in opdata.ways if whid!=crid
		)
	]
	if len(candidates)<=0:
		osmcmd.fail('ERROR: no way that crosses all other ways')
	elif len(candidates)>1:
		osmcmd.fail('ERROR: multiple ways that cross all other ways')
	else:
		crid=candidates[0]
		nc,nt=makeCrossing(crid,[whid for whid in opdata.ways if whid!=crid])
		data.addcomment('added '+str(nc)+' crossings with '+str(nt)+' traffic signals')
		data.write(sys.stdout)

if __name__=='__main__':
	main()
