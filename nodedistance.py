#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	if len(sys.argv)!=4:
		return 0

	p1=osmcmd.Point.fromArgv(1)
	p2=osmcmd.Point.fromArgv(2)
	l=p1.lengthFromMeters(float(sys.argv[3]))

	pm=p1+(p2-p1).dir(l)

	data=OsmData.OsmData()
	pm.makeNode(data)
	data.addcomment("Done.")
	data.write(sys.stdout)

if __name__=='__main__':
	main()
