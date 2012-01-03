import sys
import math
import projections
import OsmData

def readPoint(n):
	lon,lat=(float(c) for c in sys.argv[n].split(','))
	return Point('lonlat',lon,lat)

def readLength(n,point):
	return Length(float(sys.argv[n]),point)

class Data:
	def __init__(self):
		self.odata=OsmData.OsmData()
	def addNode(self,point):
		id=self.odata.addnode()
		self.odata.nodes[id][OsmData.LON]=point.lon
		self.odata.nodes[id][OsmData.LAT]=point.lat
		self.odata.nodes[id][OsmData.TAG]={}
	def write(self):
		self.odata.addcomment("Done.")
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

class Vector:
	def __init__(self,x,y):
		self.x=x
		self.y=y
	def __mul__(self,length):
		return Vector(self.x*length.value,self.y*length.value)
	def unit(self):
		"""
		Make unit vector
		"""
		len=math.sqrt(self.x**2+self.y**2)
		return Vector(self.x/len,self.y/len)

class Length:
	def __init__(self,meters,point):
		self.value=meters/math.cos(math.radians(point.lat))
