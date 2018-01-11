import sys
import math
import projections
import OsmData

def readPoint(n):
	lon,lat=(float(c) for c in sys.argv[n].split(','))
	return Point('lonlat',lon,lat)

def readLength(n,point):
	return Length(float(sys.argv[n]),point)

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
def makePointFromNode(node):
	return Point('latlon',node[OsmData.LAT],node[OsmData.LON])

# TODO put to Data class
def makePointsFromWay(way,data):
	return [Point('latlon',waynode[OsmData.LAT],waynode[OsmData.LON]) for waynode in (
		data.nodes[id] for id in way[OsmData.REF]
	)]

# TODO put to Data class
def makeNodeFromPoint(data,pt):
	id=data.addnode()
	data.nodes[id][OsmData.LON]=pt.lon
	data.nodes[id][OsmData.LAT]=pt.lat
	return id,data.nodes[id]

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
	def __init__(self,method,a,b):
		if method=='latlon':
			self.lat=a
			self.lon=b
		elif method=='lonlat':
			self.lon=a
			self.lat=b
		elif method=='xy':
			self.x=a
			self.y=b
		else:
			raise Exception('invalid point init method')
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
		return Point('xy',self.x+vector.x,self.y+vector.y)
	def __sub__(self,other):
		return Vector(self.x-other.x,self.y-other.y)
	def __eq__(self,other):
		return self.x==other.x and self.y==other.y
	def __str__(self):
		return '('+str(self.x)+','+str(self.y)+')'
	# def sideOfSegment(self,p,q):
	# 	s=self
	# 	return math.sign((p.x*p.y+p.y*s.x+q.x*s.y)-(s.x*q.y+p.y*q.x+p.x*s.y))

class Vector:
	def __init__(self,x,y):
		self.x=x
		self.y=y
	def __mul__(self,scalar):
		return Vector(self.x*scalar,self.y*scalar)
	def dir(self):
		return Direction(self)
	def unit(self):
		len=math.sqrt(self.x**2+self.y**2)
		return Vector(self.x/len,self.y/len)
	def rot90(self):
		return Vector(-self.y,self.x)

class Direction:
	def __init__(self,vector):
		len=math.sqrt(vector.x**2+vector.y**2)
		self.x=vector.x/len
		self.y=vector.y/len
	def __mul__(self,length):
		return Vector(self.x*length.value,self.y*length.value)

class Length:
	def __init__(self,metersOrVector,point=None):
		if isinstance(metersOrVector,Vector):
			vector=metersOrVector
			self.value=math.sqrt(vector.x**2+vector.y**2)
		else:
			meters=metersOrVector
			self.value=meters/math.cos(math.radians(point.lat))
	def __lt__(self,other):
		return self.value<other.value
