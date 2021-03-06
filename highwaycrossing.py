#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	def segmentsCross(s1,s2):
		a,b=s1.intersect(s2)
		return (a,b) if a>0 and a<1 and b>0 and b<1 else None
	def waysCross(crid,whid):
		return any(
			segmentsCross(crSegment,whSegment)
			for crSegment in osmcmd.Chain.fromWayId(crid,data).segments
			for whSegment in osmcmd.Chain.fromWayId(whid,data).segments
		)
	def makeCrossing(crid,whids):
		counts={'n':0,'t':0,'u':0,'j':0}
		crway=data.ways[crid]
		crway[OsmData.ACTION]=OsmData.MODIFY
		if 'highway' not in crway[OsmData.TAG]:
			crway[OsmData.TAG]['highway']='footway'
		if crway[OsmData.TAG]['highway']=='footway' and 'footway' not in crway[OsmData.TAG]:
			crway[OsmData.TAG]['footway']='crossing'
		for whid in whids:
			whway=data.ways[whid]
			def attemptCrossTwoWays():
				for cri,crSegment in enumerate(osmcmd.Chain.fromWayId(crid,data).segments):
					for whi,whSegment in enumerate(osmcmd.Chain.fromWayId(whid,data).segments):
						ls=segmentsCross(crSegment,whSegment)
						if not ls: continue

						n1=data.nodes[data.ways[whid][OsmData.REF][whi]]
						n2=data.nodes[data.ways[whid][OsmData.REF][whi+1]]
						counts['n']+=1
						crl,whl=ls
						newid,newnode=crSegment.displace(crl).makeNode(data)
						crway[OsmData.REF].insert(cri+1,newid)
						whway[OsmData.ACTION]=OsmData.MODIFY
						whway[OsmData.REF].insert(whi+1,newid)

						if whway[OsmData.TAG].get('highway')=='footway':
							counts['j']+=1
						elif (	n1[OsmData.TAG].get('highway')=='traffic_signals' or
							n2[OsmData.TAG].get('highway')=='traffic_signals' or
							n1[OsmData.TAG].get('crossing')=='traffic_signals' or
							n2[OsmData.TAG].get('crossing')=='traffic_signals'
						):
							counts['t']+=1
							newnode[OsmData.TAG]['highway']='crossing'
							newnode[OsmData.TAG]['crossing']='traffic_signals'
						else:
							counts['u']+=1
							newnode[OsmData.TAG]['highway']='crossing'
							newnode[OsmData.TAG]['crossing']='uncontrolled'
						return
			attemptCrossTwoWays()
		return counts

	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)

	if len(opdata.ways)==2:
		candidates=[
			crid for crid,crway in opdata.ways.items() if crway[OsmData.TAG].get('highway')=='footway'
		]
		if not candidates:
			candidates=[
				crid for crid,crway in opdata.ways.items() if not crway[OsmData.TAG]
			]
	else:
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
		counts=makeCrossing(crid,[whid for whid in opdata.ways if whid!=crid])
		data.addcomment('added '+str(counts['n'])+' nodes: '+str(counts['t'])+' traffic signals, '+str(counts['u'])+' uncontrolled, '+str(counts['j'])+' footway joints')
		data.write(sys.stdout)

if __name__=='__main__':
	main()
