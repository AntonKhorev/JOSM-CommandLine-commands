#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import OsmData
import osmcmd
import shootnodetoway

def main():
	try:
		data,id1,id2=shootnodetoway.sntw()
		data.nodes[id1][OsmData.ACTION]=OsmData.MODIFY
		data.nodes[id1][OsmData.TAG].update({'public_transport':'platform'})
		data.nodes[id2][OsmData.TAG].update({'public_transport':'stop_position'})
		data.addcomment('Done')
		data.write(sys.stdout)
	except:
		resultdata=osmcmd.Data()
		resultdata.write('Impossible')

if __name__=='__main__':
	main()
