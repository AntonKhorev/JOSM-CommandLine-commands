#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	data=osmcmd.readData()
	nrdata=osmcmd.readData()
	relid,rel=next(iter(nrdata.relations.items()))

	if rel[OsmData.TAG].get('type')=='public_transport' and rel[OsmData.TAG].get('public_transport')=='stop_area':
		n=0
		for id,node in nrdata.nodes.items():
			if node[OsmData.TAG].get('public_transport')=='stop_position':
				rel[OsmData.REF][OsmData.NODES].append((id,'stop'))
				n+=1
			elif node[OsmData.TAG].get('public_transport')=='platform':
				rel[OsmData.REF][OsmData.NODES].append((id,'platform'))
				n+=1
		if n>0:
			rel[OsmData.ACTION]=OsmData.MODIFY
			nrdata.addcomment(str(n)+' stops/platforms added to stop area')
			nrdata.write(sys.stdout)
		else:
			resultdata=osmcmd.Data()
			resultdata.write('WARNING: no stops/platforms added to stop area')
	elif rel[OsmData.TAG].get('type')=='route':
		ns=np=0
		for id,node in nrdata.nodes.items():
			if node[OsmData.TAG].get('public_transport')=='stop_position':
				ns+=1
				stopid=id
				stopnode=node
			elif node[OsmData.TAG].get('public_transport')=='platform':
				np+=1
				platformid=id
				platformnode=node
		if np!=1 or ns!=1:
			resultdata=osmcmd.Data()
			resultdata.write('ERROR: need exactly one stop and one platform to add to route')
		isempty=len(rel[OsmData.REF][OsmData.NODES])<=0
		rel[OsmData.ACTION]=OsmData.MODIFY
		rel[OsmData.REF][OsmData.NODES][0:0]=[(stopid,'stop'),(platformid,'platform')]
		transport=rel[OsmData.TAG].get('route')
		if transport in ('bus','trolleybus','share_taxi'):
			if stopnode[OsmData.TAG].get(transport)!='yes':
				stopnode[OsmData.ACTION]=OsmData.MODIFY
				stopnode[OsmData.TAG][transport]='yes'
			if platformnode[OsmData.TAG].get('highway')!='bus_stop':
				platformnode[OsmData.ACTION]=OsmData.MODIFY
				platformnode[OsmData.TAG]['highway']='bus_stop'
		elif transport=='tram':
			if stopnode[OsmData.TAG].get(transport)!='yes' or stopnode[OsmData.TAG].get('railway')!='tram_stop':
				stopnode[OsmData.ACTION]=OsmData.MODIFY
				stopnode[OsmData.TAG][transport]='yes'
				stopnode[OsmData.TAG]['railway']='tram_stop'
		if isempty:
			nrdata.addcomment("stop added at the beginning of route with no stops")
		else:
			nrdata.addcomment("WARNING: stop order wasn't determined - stop added at the beginning")
		nrdata.write(sys.stdout)
	else:
		resultdata=osmcmd.Data()
		resultdata.write('ERROR: unsupported relation type')

if __name__=='__main__':
	main()
