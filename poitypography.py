#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import OsmData
import osmcmd

def processPoi(poi):
	for tag in (t+s for t in ('operator','name','alt_name') for s in ('',':ru')):
		if tag not in poi[OsmData.TAG]: continue
		def sub(regex,repl):
			v=poi[OsmData.TAG][tag]
			v2,n=re.subn(regex,repl,v)
			if n>0:
				poi[OsmData.ACTION]=OsmData.MODIFY
				poi[OsmData.TAG][tag]=v2
		sub(r'"(.*)"',r'«\1»')
		sub(r'№\s*',r'№ ')
		sub(r'\s+[-—]\s+',' — ')

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
