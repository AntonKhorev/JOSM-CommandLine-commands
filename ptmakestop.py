#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd
import shoot

def main():
	data=osmcmd.readData()
	nwdata=osmcmd.readData()
	data.mergedata(nwdata)
	wayid=next(iter(nwdata.ways))
	n=0
	for platformid in nwdata.nodes:
		stopid=shoot.sntw(data,platformid,wayid)
		if stopid is None:
			continue
		n+=1
		plnode=data.nodes[platformid]
		stnode=data.nodes[stopid]
		plnode[OsmData.ACTION]=OsmData.MODIFY
		plnode[OsmData.TAG].update({'public_transport':'platform'})
		stnode[OsmData.TAG].update({'public_transport':'stop_position'})
		if 'name' not in stnode[OsmData.TAG] and 'name' in plnode[OsmData.TAG]:
			stnode[OsmData.TAG]['name']=plnode[OsmData.TAG]['name']

	if n>0:
		data.addcomment(str(n)+' stops created')
		data.write(sys.stdout)
	else:
		osmcmd.fail('WARNING: no stops created')

if __name__=='__main__':
	main()
