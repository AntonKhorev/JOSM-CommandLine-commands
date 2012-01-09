#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd
import shootnodetoway

def main():
	data=osmcmd.readData()
	nwdata=osmcmd.readData()
	data.mergedata(nwdata)
	wayid=next(iter(nwdata.ways))
	n=0
	for platformid in nwdata.nodes:
		stopid=shootnodetoway.sntw(data,platformid,wayid)
		if stopid is None:
			continue
		n+=1
		data.nodes[platformid][OsmData.ACTION]=OsmData.MODIFY
		data.nodes[platformid][OsmData.TAG].update({'public_transport':'platform'})
		data.nodes[stopid][OsmData.TAG].update({'public_transport':'stop_position'})

	if n>0:
		data.addcomment(str(n)+' stops created')
		data.write(sys.stdout)
	else:
		resultdata=osmcmd.Data()
		resultdata.write('WARNING: no stops created')

if __name__=='__main__':
	main()
