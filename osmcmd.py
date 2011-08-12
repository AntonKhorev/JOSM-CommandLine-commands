import sys
import math
import projections
import OsmData

def readPoint(n):
	return projections.from4326(
		(float(c) for c in sys.argv[n].split(',')),
		"EPSG:3857"
	)

def readLength(n,point):
	lat=projections.to4326(point,"EPSG:3857")[1]
	return float(sys.argv[n])/math.cos(math.radians(lat))

class data:
	def __init__(self):
		self.odata=OsmData.OsmData()
	def addNode(self,point):
		p=projections.to4326(point,"EPSG:3857")
		id=self.odata.addnode()
		self.odata.nodes[id][OsmData.LON]=p[0]
		self.odata.nodes[id][OsmData.LAT]=p[1]
		self.odata.nodes[id][OsmData.TAG]={}
	def write(self):
		self.odata.addcomment("Done.")
		self.odata.write(sys.stdout)
