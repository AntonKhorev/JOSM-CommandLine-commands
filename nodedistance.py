#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import osmcmd

def main():
	if len(sys.argv)!=4:
		return 0

	p1=osmcmd.readPoint(1)
	p2=osmcmd.readPoint(2)
	l=osmcmd.readLength(3,p1)

	dv=(p2[0]-p1[0],p2[1]-p1[1])
	dvl=math.sqrt(dv[0]**2+dv[1]**2)
	dvn=(dv[0]/dvl,dv[1]/dvl)
	pm=(p1[0]+dvn[0]*l,p1[1]+dvn[1]*l)

	td=osmcmd.data()
	td.addNode(pm)
	td.write()

if __name__=='__main__':
	main()
