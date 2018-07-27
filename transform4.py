#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def main():
	if len(sys.argv)!=1+4*2:
		return 0

	p0=osmcmd.Point.fromArgv(1)
	t0=osmcmd.Point.fromArgv(2)
	p1=osmcmd.Point.fromArgv(3)
	t1=osmcmd.Point.fromArgv(4)
	p2=osmcmd.Point.fromArgv(5)
	t2=osmcmd.Point.fromArgv(6)
	p3=osmcmd.Point.fromArgv(7)
	t3=osmcmd.Point.fromArgv(8)

	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)

	epsilon=10e-4
	nIterations=100

	def transformPoint(p):
		a0=0.5
		b0=0.5
		# TODO make symmetric eqn
		# (p1-p0)*a+(p3-p0)*b=(p-p0)+(p3-p2)*a*b+(p1-p0)*a*b
		for i in range(nIterations):
			a1,b1=osmcmd.solveLinEqns([
				[(p1-p0).x,(p3-p0).x,(p-p0).x+(p3-p2).x*a0*b0+(p1-p0).x*a0*b0],
				[(p1-p0).y,(p3-p0).y,(p-p0).y+(p3-p2).y*a0*b0+(p1-p0).y*a0*b0],
			])
			if (a0-a1)**2+(b0-b1)**2<epsilon**2:
				break
			a0=a1
			b0=b1
		return t0+(t1-t0)*a1+(t3-t0)*b1+(t0-t1)*a1*b1+(t2-t3)*a1*b1

	for nodeId in data.nodes:
		node=data.nodes[nodeId]
		point=osmcmd.Point.fromNode(node)
		newPoint=transformPoint(point)
		newPoint.setNode(node)

	data.addcomment("Done.")
	data.write(sys.stdout)

if __name__=='__main__':
	main()
