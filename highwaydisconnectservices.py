#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import OsmData
import osmcmd

def main():
	data=osmcmd.readData()
	highwayData=osmcmd.readData()
	serviceNodes={}
	for id,way in highwayData.ways.items():
		if way[OsmData.TAG].get('highway')!='service': continue
		for nodeId in way[OsmData.REF]:
			serviceNodes[nodeId]=True
	for id,way in highwayData.ways.items():
		if way[OsmData.TAG].get('highway') not in (
			'residential','unclassified','tertiary','secondary','primary'
		): continue
		# assume street is not circular
		i=1
		while i<len(way[OsmData.REF])-1:
			if way[OsmData.REF][i] in serviceNodes:
				way[OsmData.ACTION]=OsmData.MODIFY
				del way[OsmData.REF][i]
			else:
				i+=1
	highwayData.write(sys.stdout)

if __name__=='__main__':
	main()
