#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import osmcmd

def main():
	if len(sys.argv)!=4:
		return 0

	p1=osmcmd.readPoint(1)
	p2=osmcmd.readPoint(2)
	pr=sys.argv[3]
	if '|' in pr:
		a,b=(float(t) for t in pr.split('|'))
		w1=b/(a+b)
		w2=a/(a+b)
	else:
		w2=float(pr)
		w1=1-w2

	pm=(
		p1[0]*w1+p2[0]*w2,
		p1[1]*w1+p2[1]*w2,
	)

	td=osmcmd.data()
	td.addNode(pm)
	td.write()

if __name__=='__main__':
	main()
