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
					return preceding_stopid, None if sure or all(p[0] not in wnids for p in refnodes) else "Ambiguous way direction"
				if wnid in [p[0] for p in refnodes]:
					preceding_stopid=wnid
			prev_end_id=wnids[-1]
		return None,"Dangling currently added stop"
	preceding_stopid,warning_reason=detPrecedingStopId()

	warning_reasons=[warning_reason] if warning_reason is not None else []
	if any(p[0] not in (
		id for p in refways for id in data.ways[p[0]][OsmData.REF]
	) for p in refnodes if p[1].startswith('stop')):
		warning_reasons.append("Dangling stops added before")
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
	data.mergedata(nrdata)
	relid=next(iter(nrdata.relations))
	rel=data.relations[relid]

	if rel[OsmData.TAG].get('type')=='public_transport' and rel[OsmData.TAG].get('public_transport')=='stop_area':
		n=0
		for id in nrdata.nodes:
			node=data.nodes[id]
			if node[OsmData.TAG].get('public_transport')=='stop_position':
				rel[OsmData.REF][OsmData.NODES].append((id,'stop'))
			elif node[OsmData.TAG].get('public_transport')=='platform':
				rel[OsmData.REF][OsmData.NODES].append((id,'platform'))
			else:
				continue
			n+=1
			if 'name' in rel[OsmData.TAG] and 'name' not in node[OsmData.TAG]:
				node[OsmData.ACTION]=OsmData.MODIFY
				node[OsmData.TAG]['name']=rel[OsmData.TAG]['name']
		if n>0:
			rel[OsmData.ACTION]=OsmData.MODIFY
			data.addcomment(str(n)+' stops/platforms added to stop area')
			#data.write(sys.stdout)
			writeHack(data,sys.stdout)
		else:
			osmcmd.fail('WARNING: no stops/platforms added to stop area')
	elif rel[OsmData.TAG].get('type')=='route':
		ns=np=0
		for id in nrdata.nodes:
			node=data.nodes[id]
			if node[OsmData.TAG].get('public_transport')=='stop_position':
				ns+=1
				stopid=id
				stopnode=node
			elif node[OsmData.TAG].get('public_transport')=='platform':
				np+=1
				platformid=id
				platformnode=node
		if np!=1 or ns!=1:
			osmcmd.fail('ERROR: need exactly one stop and one platform to add to route')
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
		data.addcomment(reason)
		#data.write(sys.stdout)
		writeHack(data,sys.stdout)
	else:
		osmcmd.fail('ERROR: unsupported relation type')

if __name__=='__main__':
	main()
