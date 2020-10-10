#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import OsmData
import osmcmd

def inScope(way,scope):
	tags=way[OsmData.TAG]
	if 'highway' not in tags:
		return False
	hw=tags['highway']
	for key in scope:
		if key=='street':
			if hw in ('primary','secondary','tertiary','unclassified','residential'):
				return True
		elif key=='footway':
			if hw=='footway' and tags.get('footway') not in ('sidewalk','crossing'):
				return True
		elif key=='sidewalk':
			if hw=='footway' and tags.get('footway')=='sidewalk':
				return True
		elif key=='crossing':
			if hw=='footway' and tags.get('footway')=='crossing':
				return True
		else:
			if hw==key:
				return True
	return False

def main():
	data=osmcmd.readData()
	highwayData=osmcmd.readData()
	data.mergedata(highwayData)
	formula=sys.argv[1]
	match=re.match(r'([a-z,]+)(<?)([-+]?)(>?)([a-z,]+)',formula)
	if not match:
		osmcmd.fail('ERROR: invalid syntax')
		return
	outerString,toOuter,newNodeFlag,toInner,innerString=match.groups()
	outers=outerString.split(',')
	inners=innerString.split(',')
	if toOuter and toInner:
		osmcmd.fail('WARNING: ordered not to disconnect')
		return
	if toOuter: outers,inners=inners,outers
	disconnectNodes={}
	for id,way in highwayData.ways.items():
		if not inScope(way,inners): continue
		for nodeId in way[OsmData.REF]:
			disconnectNodes[nodeId]=None
	for id in highwayData.ways:
		way=data.ways[id]
		if not inScope(way,outers): continue
		# assume street is not circular
		i=0
		while i<len(way[OsmData.REF]):
			isEdge=(i==0 or i==len(way[OsmData.REF])-1)
			oldNodeId=way[OsmData.REF][i]
			if oldNodeId in disconnectNodes:
				way[OsmData.ACTION]=OsmData.MODIFY
				if (isEdge and newNodeFlag!='-') or newNodeFlag=='+':
					if disconnectNodes[oldNodeId]:
						way[OsmData.REF][i]=disconnectNodes[oldNodeId]
					else:
						newNodeId=data.addnode()
						data.nodes[newNodeId][OsmData.LON]=data.nodes[oldNodeId][OsmData.LON]
						data.nodes[newNodeId][OsmData.LAT]=data.nodes[oldNodeId][OsmData.LAT]
						way[OsmData.REF][i]=disconnectNodes[oldNodeId]=newNodeId
					i+=1
				else:
					del way[OsmData.REF][i]
			else:
				i+=1
	data.write(sys.stdout)

if __name__=='__main__':
	main()
