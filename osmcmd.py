import sys
import math
import projections
import OsmData

def readLength(n,point):
	return point.lengthFromMeters(float(sys.argv[n]))

def readData():
	data=OsmData.OsmData()
	data.read(sys.stdin)
	return data

def solveLinEqns(m):
	det =m[0][0]*m[1][1]-m[0][1]*m[1][0]
	det0=m[0][2]*m[1][1]-m[0][1]*m[1][2]
	det1=m[0][0]*m[1][2]-m[0][2]*m[1][0]
	if det==0:
		return float('inf'),float('inf')
	else:
		return det0/det,det1/det

# returns (displacement along pf1-pf2 line, displacement along pt1-pt2 line)
def shoot(pf1,pf2,pt1,pt2): # "from" and "to" line segments by their endpoints
	return solveLinEqns((
		(pf2.x-pf1.x,pt1.x-pt2.x,pt1.x-pf1.x),
		(pf2.y-pf1.y,pt1.y-pt2.y,pt1.y-pf1.y),
	))

# TODO put to Data class
def makePointsFromWay(way,data):
	return [Point.fromNode(waynode) for waynode in (
		data.nodes[id] for id in way[OsmData.REF]
	)]

def fail(msg):
	resultdata=Data()
	resultdata.write(msg)

class Data:
	def __init__(self):
		self.odata=OsmData.OsmData()
	def addNode(self,point):
		id=self.odata.addnode()
		self.odata.nodes[id][OsmData.LON]=point.lon
		self.odata.nodes[id][OsmData.LAT]=point.lat
		self.odata.nodes[id][OsmData.TAG]={}
	def write(self,msg="Done."):
		self.odata.addcomment(msg)
		self.odata.write(sys.stdout)

class Point:
	def __init__(self,x,y):
		self.x=x
		self.y=y
	@classmethod
	def fromLatLon(cls,lat,lon):
		point=cls(0,0)
		del point.x
		del point.y
		point.lat=lat
		point.lon=lon
		return point
	@classmethod
	def fromLonLat(cls,lon,lat):
		return cls.fromLatLon(lat,lon)
	@classmethod
	def fromArgv(cls,n):
		lon,lat=(float(c) for c in sys.argv[n].split(','))
		return cls('lonlat',lon,lat)
	@classmethod
	def fromNode(cls,node):
		return cls.fromLatLon(node[OsmData.LAT],node[OsmData.LON])
	def __getattr__(self,name):
		if name=='x' or name=='y':
			self.x,self.y=projections.from4326((self.lon,self.lat),"EPSG:3857")
			return getattr(self,name)
		elif name=='lat' or name=='lon':
			self.lon,self.lat=projections.to4326((self.x,self.y),"EPSG:3857")
			return getattr(self,name)
		else:
			raise AttributeError('invalid point attr "'+name+'"')
	def __add__(self,vector):
		return Point(self.x+vector.x,self.y+vector.y)
	def __sub__(self,other):
		return Vector(self.x-other.x,self.y-other.y)
	def __eq__(self,other):
		return self.x==other.x and self.y==other.y
	def __str__(self):
		return '('+str(self.x)+','+str(self.y)+')'
	def lengthFromMeters(self,meters):
		return meters/math.cos(math.radians(self.lat))
	# def sideOfSegment(self,p,q):
	# 	s=self
	# 	return math.sign((p.x*p.y+p.y*s.x+q.x*s.y)-(s.x*q.y+p.y*q.x+p.x*s.y))
	def setNode(self,node):
		if node.get(OsmData.ACTION)!=OsmData.CREATE:
			node[OsmData.ACTION]=OsmData.MODIFY
		node[OsmData.LON]=self.lon
		node[OsmData.LAT]=self.lat
	def makeNode(self,data):
		id=data.addnode()
		self.setNode(data.nodes[id])
		return id,data.nodes[id]

class Vector:
	def __init__(self,x,y):
		self.x=x
		self.y=y
	def __getattr__(self,name):
		if name=='length':
			self.length=math.sqrt(self.x**2+self.y**2)
			return getattr(self,name)
		else:
			raise AttributeError('invalid vector attr "'+name+'"')
	def __mul__(self,scalar):
		return Vector(self.x*scalar,self.y*scalar)
	def dir(self,length=1): # used to return Direction class, now returns Vector of specified length with the same direction
		s=length/self.length
		return Vector(self.x*s,self.y*s)
	def rot90(self):
		return Vector(-self.y,self.x)
