#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd
import functools

def rewireWay(data,rewireid,fromid,toid,tosidewalkid):
	nnodes=0
	rw=data.ways[rewireid]
	fw=data.ways[fromid]
	tw=data.ways[toid]
	def getIntersections():
		return ((ri,fi,rid)
			for ri,rid in enumerate(rw[OsmData.REF])
			for fi,fid in enumerate(fw[OsmData.REF])
			if rid==fid
		)
	for ri,fi,iid in getIntersections():
		if ri==0:
			rid2=iid
			rid1=rw[OsmData.REF][1]
		elif ri==len(rw[OsmData.REF])-1:
			rid2=iid
			rid1=rw[OsmData.REF][-2]
		else:
			continue # TODO

		rpt1=osmcmd.makePointFromNode(data.nodes[rid1])
		rpt2=osmcmd.makePointFromNode(data.nodes[rid2])
		l,ti=functools.reduce(min,
			((l,ti) for ti,(l,s) in (
				(i,osmcmd.shoot(rpt1,rpt2,
					osmcmd.makePointFromNode(data.nodes[tw[OsmData.REF][i]]),
					osmcmd.makePointFromNode(data.nodes[tw[OsmData.REF][i+1]])
				)) for i in range(len(tw[OsmData.REF])-1)
			) if s>0 and s<1 and l>0),
			(float('inf'),None)
		)
		if ti is None:
			continue

		rpt3=rpt1+(rpt2-rpt1)*l
		# remove node 'from'
		fw[OsmData.ACTION]=OsmData.MODIFY
		fw[OsmData.REF].pop(fi)
		# move node
		data.nodes[iid][OsmData.ACTION]=OsmData.MODIFY
		data.nodes[iid][OsmData.LAT]=rpt3.lat
		data.nodes[iid][OsmData.LON]=rpt3.lon
		# add node 'to'
		tw[OsmData.ACTION]=OsmData.MODIFY
		tw[OsmData.REF].insert(ti+1,iid)
		# TODO sidewalk
		nnodes+=1
	return nnodes

def main():
	data=osmcmd.readData()
	rewiredata=osmcmd.readData()
	data.mergedata(rewiredata)
	fromdata=osmcmd.readData()
	data.mergedata(fromdata)
	todata=osmcmd.readData()
	data.mergedata(todata)

	fromid=next(iter(fromdata.ways))

	toroadid=tosidewalkid=None
	for toid,toway in todata.ways.items():
		if toway[OsmData.TAG].get('highway')=='footway':
			tosidewalkid=toid
		else:
			toroadid=toid
	if toroadid is None and tosidewalkid is not None:
		toroadid=tosidewalkid
		tosidewalkid=None
	if toroadid is None:
		osmcmd.fail('ERROR: no way to rewire to')
		return

	n=0
	for rewireid in rewiredata.ways:
		n+=rewireWay(data,rewireid,fromid,toroadid,tosidewalkid)
	if n==0:
		osmcmd.fail('WARNING: nothing changed')
	else:
		data.addcomment(str(n)+' nodes rewired')
		data.write(sys.stdout)

if __name__=='__main__':
	main()
