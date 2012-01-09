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
	else:
		resultdata=osmcmd.Data()
		resultdata.write('ERROR: unsupported relation type')

if __name__=='__main__':
	main()
