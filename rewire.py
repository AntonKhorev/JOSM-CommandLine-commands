#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd
import functools

def rewireWay(data,rewireid,fromid,toroadid,tosidewalkid):
	nnodes=0
	rw=data.ways[rewireid]
	fw=data.ways[fromid]
	trw=data.ways[toroadid]
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
		def shootToWay(tw):
			return functools.reduce(min,
				((l,ti) for ti,(l,s) in (
					(i,osmcmd.shoot(rpt1,rpt2,
						osmcmd.makePointFromNode(data.nodes[tw[OsmData.REF][i]]),
						osmcmd.makePointFromNode(data.nodes[tw[OsmData.REF][i+1]])
					)) for i in range(len(tw[OsmData.REF])-1)
				) if s>0 and s<1 and l>0),
				(float('inf'),None)
			)
		lr,tri=shootToWay(trw)
		if tri is None:
			continue

		rpt3=rpt1+(rpt2-rpt1)*lr
		# remove node 'from'
		fw[OsmData.ACTION]=OsmData.MODIFY
		fw[OsmData.REF].pop(fi)
		# move node
		data.nodes[iid][OsmData.ACTION]=OsmData.MODIFY
		data.nodes[iid][OsmData.LAT]=rpt3.lat
		data.nodes[iid][OsmData.LON]=rpt3.lon
		# add node 'to'
		trw[OsmData.ACTION]=OsmData.MODIFY
		trw[OsmData.REF].insert(tri+1,iid)

		nnodes+=1

		# sidewalk
		if tosidewalkid is None:
			continue
		tsw=data.ways[tosidewalkid]
		ls,tsi=shootToWay(tsw)
		if ls>lr:
			continue
		# add new node at intersection w/ sidewalk
		rpt4=rpt1+(rpt2-rpt1)*ls
		nid=data.addnode()
		data.nodes[nid][OsmData.LON]=rpt4.lon
		data.nodes[nid][OsmData.LAT]=rpt4.lat
		tsw[OsmData.ACTION]=OsmData.MODIFY
		tsw[OsmData.REF].insert(tsi+1,nid)
		rw[OsmData.ACTION]=OsmData.MODIFY
		if 'highway' in rw[OsmData.TAG] and rw[OsmData.TAG]!='footway' and rw[OsmData.TAG].get('foot')!='no':
			# split way
			nid2=data.addway()
			data.ways[nid2][OsmData.TAG]=rw[OsmData.TAG].copy()
			data.ways[nid2][OsmData.TAG]['foot']='no'
			data.ways[nid2][OsmData.REF] = [iid,nid] if ri==0 else [nid,iid]
			rw[OsmData.REF][0 if ri==0 else -1]=nid
		else:
			# simply insert node
			rw[OsmData.REF].insert(1 if ri==0 else -1, nid)

	return nnodes

def rewireRestriction(data,rewireid,fromid,toid):
	nmembers=0
	rel=data.relations[rewireid]
	for i,(wid,wrole) in enumerate(rel[OsmData.REF][OsmData.WAYS]):
		if wid!=fromid or wrole not in ('from','to'):
			continue
		rel[OsmData.ACTION]=OsmData.MODIFY
		rel[OsmData.REF][OsmData.WAYS][0]=(toid,wrole)
		nmembers+=1
	return nmembers

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

	nn=nm=0
	for rewireid in rewiredata.ways:
		nn+=rewireWay(data,rewireid,fromid,toroadid,tosidewalkid)
	for rewireid,rewirerel in rewiredata.relations.items():
		if rewirerel[OsmData.TAG].get('type')=='restriction':
			nm+=rewireRestriction(data,rewireid,fromid,toroadid)
	if nn==0 and nm==0:
		osmcmd.fail('WARNING: nothing changed')
	else:
		data.addcomment(str(nn)+' nodes rewired, '+str(nm)+' relation members changed')
		data.write(sys.stdout)

if __name__=='__main__':
	main()
