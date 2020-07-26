#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import fractions
import OsmData
import osmcmd

def main():
	if len(sys.argv)!=4:
		return 0

	p1=osmcmd.Point.fromArgv(1)
	p2=osmcmd.Point.fromArgv(2)
	pr=sys.argv[3]
	if '|' in pr:
		a,b=(float(t) for t in pr.split('|'))
		w=a/(a+b)
	elif ':' in pr:
		a,b=(float(t) for t in pr.split(':'))
		w=a/(a+b)
	else:
		w=float(fractions.Fraction(pr))

	pm=p1+(p2-p1)*w

	data=OsmData.OsmData()
	pm.makeNode(data)
	data.addcomment("Done.")
	data.write(sys.stdout)

if __name__=='__main__':
	main()
