#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	if len(sys.argv)!=1+3*2:
		return 0

	p1=osmcmd.Point.fromArgv(1)
	t1=osmcmd.Point.fromArgv(2)
	p2=osmcmd.Point.fromArgv(3)
	t2=osmcmd.Point.fromArgv(4)
	p3=osmcmd.Point.fromArgv(5)
	t3=osmcmd.Point.fromArgv(6)

	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)

	def transformPoint(p):
		a,b=osmcmd.solveLinEqns([
			[(p2-p1).x,(p3-p1).x,(p-p1).x],
			[(p2-p1).y,(p3-p1).y,(p-p1).y],
		])
		return t1+(t2-t1)*a+(t3-t1)*b

	for nodeId in data.nodes:
		node=data.nodes[nodeId]
		point=osmcmd.Point.fromNode(node)
		newPoint=transformPoint(point)
		newPoint.setNode(node)

	data.addcomment("Done.")
	data.write(sys.stdout)

if __name__=='__main__':
	main()
