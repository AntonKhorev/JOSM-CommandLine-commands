#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	data=osmcmd.readData()
	nodedata=osmcmd.readData()

	while data.relations.get(data.currrelationid)!=None:
		data.currrelationid-=1
	rel=data.relations[data.currrelationid]={
		OsmData.ACTION:OsmData.CREATE,
		OsmData.REF:{
			OsmData.NODES:[],
			OsmData.WAYS:[],
			OsmData.RELATIONS:[],
		},
		OsmData.TAG:{
			'type':'public_transport',
			'public_transport':'stop_area',
		}
	}
	for id,node in nodedata.nodes.items():
		if node[OsmData.TAG].get('public_transport')=='stop_position':
			rel[OsmData.REF][OsmData.NODES].append((id,'stop'))
		elif node[OsmData.TAG].get('public_transport')=='platform':
			rel[OsmData.REF][OsmData.NODES].append((id,'platform'))
		if 'name' in node[OsmData.TAG]:
			rel[OsmData.TAG]['name']=node[OsmData.TAG]['name']

	if len(rel[OsmData.REF][OsmData.NODES])<=0:
		resultdata=osmcmd.Data()
		resultdata.write('No stops/platforms provided')
	else:
		data.addcomment('Done')
		data.write(sys.stdout)

if __name__=='__main__':
	main()
