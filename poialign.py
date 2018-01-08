#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import OsmData
import osmcmd

def getClosestPointOnWay(fpt,waypts):
	mi=None
	ml2=float('inf')
	mp=None
	# try segment endpoints
	for wpt in waypts:
		v=wpt-fpt
		l2=v.x**2+v.y**2
		if l2<ml2:
			ml2=l2
			mp=wpt
	# try points inside segments
	ml=math.sqrt(ml2)
	for wp1,wp2 in [(waypts[i],waypts[i+1]) for i in range(len(waypts)-1)]:
		fp1=fpt
		dwp=wp2-wp1
		fp2=fp1+osmcmd.Vector(-dwp.y,dwp.x).dir() # fake point to make perpendicular line
		l,s=osmcmd.shoot(fp1,fp2,wp1,wp2)
		if s<0 or s>1:
			continue
		if abs(l)<ml:
			ml=abs(l)
			mp=wp1+(wp2-wp1)*s
	return mp

def main():
	data=osmcmd.readData()
	opdata=osmcmd.readData()
	data.mergedata(opdata)
	if len(opdata.ways)<1:
		osmcmd.fail('ERROR: no way to align POIs')
	if len(opdata.ways)>1:
		osmcmd.fail('ERROR: too many way to align POIs')
	waypts=[osmcmd.makePointsFromWay(data.ways[wid],data) for wid in opdata.ways][0]
	for pid in opdata.nodes:
		fpt=osmcmd.makePointFromNode(data.nodes[pid])
		wpt=getClosestPointOnWay(fpt,waypts)
		tpt=wpt+(fpt-wpt).dir()*osmcmd.Length(2,wpt)
		data.nodes[pid][OsmData.ACTION]=OsmData.MODIFY
		data.nodes[pid][OsmData.LON]=tpt.lon
		data.nodes[pid][OsmData.LAT]=tpt.lat
	data.write(sys.stdout)

if __name__=='__main__':
	main()
