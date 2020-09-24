#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import OsmData
import osmcmd

def main():
	data=osmcmd.readData()
	poidata=osmcmd.readData()
	for id,poi in poidata.nodes.items():
		if 'operator' in poi[OsmData.TAG]:
			op=poi[OsmData.TAG]['operator']
			op2,n=re.subn(r'"(.*)"',r'«\1»',op)
			if n>0:
				poi[OsmData.ACTION]=OsmData.MODIFY
				poi[OsmData.TAG]['operator']=op2
	poidata.write(sys.stdout)

if __name__=='__main__':
	main()
