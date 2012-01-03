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
		w=b/(a+b)
	else:
		w=1-float(pr)

	pm=p1+(p2-p1)*w

	td=osmcmd.Data()
	td.addNode(pm)
	td.write()

if __name__=='__main__':
	main()
