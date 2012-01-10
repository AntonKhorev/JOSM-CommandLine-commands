#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd

def writeHack(self,targetStream):
	targetStream.write("<osm version=\"0.6\">\n")

	# Modifying: WRITE RELATION FIRST
	for relation in self.relations.items():
		if relation[1].get(OsmData.ACTION) != OsmData.MODIFY:
			continue
		targetStream.write(self.xmlrelation(relation))
	for node in self.nodes.items():
		if node[1].get(OsmData.ACTION) != OsmData.MODIFY:
			continue
		targetStream.write(self.xmlnode(node))

	for text in self.comments:
		targetStream.write("<!--" + text + "-->\n")
	targetStream.write("</osm>")

def determineInsertPosition(data,rel,stopid):
	refnodes=rel[OsmData.REF][OsmData.NODES]
	refways=rel[OsmData.REF][OsmData.WAYS]
	if len(refnodes)<=0:
		return 0,"stop added at the beginning of route with no stops"

	def detPrecedingStopId():
		prev_end_id=None
		preceding_stopid=None
		for i,way in enumerate(data.ways[p[0]] for p in refways):
			reversed=False
			sure=False
			if way[OsmData.REF][0]==prev_end_id:
				reversed=False
				sure=True
			elif way[OsmData.REF][-1]==prev_end_id:
				reversed=True
				sure=True
			elif i<len(refways)-1:
				nextway=data.ways[refways[i+1][0]]
				if way[OsmData.REF][-1] in (nextway[OsmData.REF][0],nextway[OsmData.REF][-1]):
					reversed=False
					sure=True
				elif way[OsmData.REF][0] in (nextway[OsmData.REF][0],nextway[OsmData.REF][-1]):
					reversed=True
					sure=True
			wnids=way[OsmData.REF][::-1] if reversed else way[OsmData.REF]
			for wnid in wnids:
				if wnid==stopid:
					return preceding_stopid, sure or all(p[0] not in wnids for p in refnodes)
				if wnid in [p[0] for p in refnodes]:
					preceding_stopid=wnid
			prev_end_id=wnids[-1]
		return None,True
	preceding_stopid,sure_in_way_direction=detPrecedingStopId()

	warning_reasons=[]
	if not sure_in_way_direction:
		warning_reasons.append("Ambiguous way direction")
	if any(p[0] not in (
		id for p in refways for id in data.ways[p[0]][OsmData.REF]
	) for p in refnodes if p[1].startswith('stop')):
		warning_reasons.append("Dangling stops")
	msg_prefix="WARNING: stop order wasn't determined because of "+' and '.join(warning_reasons)+'; ' if warning_reasons else ''

	if preceding_stopid is None:
		return 0,msg_prefix+"stop added at the beginning of route"
	i=1+[p[0] for p in refnodes].index(preceding_stopid)
	while i<len(refnodes) and refnodes[i][1].startswith('platform'):
		i+=1
	if 'name' in data.nodes[preceding_stopid][OsmData.TAG]:
		return i,msg_prefix+"stop added after '"+data.nodes[preceding_stopid][OsmData.TAG]['name']+"'"
	else:
		return i,msg_prefix+"stop added at position "+str(i)

def main():
	data=osmcmd.readData()
	nrdata=osmcmd.readData()
	relid,rel=next(iter(nrdata.relations.items()))

	if rel[OsmData.TAG].get('type')=='public_transport' and rel[OsmData.TAG].get('public_transport')=='stop_area':
		n=0
		for id,node in nrdata.nodes.items():
			if node[OsmData.TAG].get('public_transport')=='stop_position':
				rel[OsmData.REF][OsmData.NODES].append((id,'stop'))
				n+=1
			elif node[OsmData.TAG].get('public_transport')=='platform':
				rel[OsmData.REF][OsmData.NODES].append((id,'platform'))
				n+=1
		if n>0:
			rel[OsmData.ACTION]=OsmData.MODIFY
			nrdata.addcomment(str(n)+' stops/platforms added to stop area')
			nrdata.write(sys.stdout)
		else:
			resultdata=osmcmd.Data()
			resultdata.write('WARNING: no stops/platforms added to stop area')
	elif rel[OsmData.TAG].get('type')=='route':
		ns=np=0
		for id,node in nrdata.nodes.items():
			if node[OsmData.TAG].get('public_transport')=='stop_position':
				ns+=1
				stopid=id
				stopnode=node
			elif node[OsmData.TAG].get('public_transport')=='platform':
				np+=1
				platformid=id
				platformnode=node
		if np!=1 or ns!=1:
			resultdata=osmcmd.Data()
			resultdata.write('ERROR: need exactly one stop and one platform to add to route')
			return
		position,reason=determineInsertPosition(data,rel,stopid)
		rel[OsmData.ACTION]=OsmData.MODIFY
		rel[OsmData.REF][OsmData.NODES][position:position]=[(stopid,'stop'),(platformid,'platform')]
		transport=rel[OsmData.TAG].get('route')
		if transport in ('bus','trolleybus','share_taxi'):
			if stopnode[OsmData.TAG].get(transport)!='yes':
				stopnode[OsmData.ACTION]=OsmData.MODIFY
				stopnode[OsmData.TAG][transport]='yes'
			if platformnode[OsmData.TAG].get('highway')!='bus_stop':
				platformnode[OsmData.ACTION]=OsmData.MODIFY
				platformnode[OsmData.TAG]['highway']='bus_stop'
		elif transport=='tram':
			if stopnode[OsmData.TAG].get(transport)!='yes' or stopnode[OsmData.TAG].get('railway')!='tram_stop':
				stopnode[OsmData.ACTION]=OsmData.MODIFY
				stopnode[OsmData.TAG][transport]='yes'
				stopnode[OsmData.TAG]['railway']='tram_stop'
		nrdata.addcomment(reason)
		#nrdata.write(sys.stdout)
		writeHack(nrdata,sys.stdout)
	else:
		resultdata=osmcmd.Data()
		resultdata.write('ERROR: unsupported relation type')

if __name__=='__main__':
	main()
