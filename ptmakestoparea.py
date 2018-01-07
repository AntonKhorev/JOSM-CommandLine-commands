#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	data=osmcmd.readData()
	nodedata=osmcmd.readData()
	data.mergedata(nodedata)

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
	name=None
	for id,node in nodedata.nodes.items():
		if 'name' in node[OsmData.TAG]:
			name=node[OsmData.TAG]['name']
	if name is not None:
		rel[OsmData.TAG]['name']=name
	for id in nodedata.nodes:
		node=data.nodes[id]
		if node[OsmData.TAG].get('public_transport')=='stop_position':
			rel[OsmData.REF][OsmData.NODES].append((id,'stop'))
		elif node[OsmData.TAG].get('public_transport')=='platform':
			rel[OsmData.REF][OsmData.NODES].append((id,'platform'))
		else:
			continue
		if name is not None and 'name' not in node[OsmData.TAG]:
			node[OsmData.ACTION]=OsmData.MODIFY
			node[OsmData.TAG]['name']=name

	if len(rel[OsmData.REF][OsmData.NODES])<=0:
		osmcmd.fail('No stops/platforms provided')
	else:
		data.addcomment('Done')
		data.write(sys.stdout)

if __name__=='__main__':
	main()
