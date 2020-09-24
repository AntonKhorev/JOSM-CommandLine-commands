#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import OsmData
import osmcmd

def processPoi(poi):
	if 'operator' in poi[OsmData.TAG]:
		op=poi[OsmData.TAG]['operator']
		op2,n=re.subn(r'"(.*)"',r'«\1»',op)
		if n>0:
			poi[OsmData.ACTION]=OsmData.MODIFY
			poi[OsmData.TAG]['operator']=op2

def main():
	data=osmcmd.readData()
	poidata=osmcmd.readData()
	for id,poi in poidata.nodes.items():
		processPoi(poi)
	for id,poi in poidata.ways.items():
		processPoi(poi)
	for id,poi in poidata.relations.items():
		processPoi(poi)
	poidata.write(sys.stdout)

if __name__=='__main__':
	main()
