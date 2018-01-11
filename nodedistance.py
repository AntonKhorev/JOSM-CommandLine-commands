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

	pm=p1+(p2-p1).dir(l)

	td=osmcmd.Data()
	td.addNode(pm)
	td.write()

if __name__=='__main__':
	main()
