import unittest
import osmcmd
import poialign

def Pt(x,y):
	return osmcmd.Point('xy',x,y)

class TestOsmCmd(unittest.TestCase):
	def testNodeDistance(self):
		p1=osmcmd.Point('latlon',59.929928003648804,30.39256987360226)
		p2=osmcmd.Point('latlon',59.93093128613418,30.397014125548477)
		len=osmcmd.Length(20,p1)
		pr=p1+(p2-p1).dir()*len
		self.assertAlmostEqual(pr.lat,59.9300018058)
		self.assertAlmostEqual(pr.lon,30.3928967912)
	def testVectorLength(self):
		p1=Pt(0,0)
		p2=Pt(3,4)
		len=osmcmd.Length(p2-p1)
		self.assertAlmostEqual(len.value,5)
	def testVectorRot90(self):
		v=osmcmd.Vector(10,0)
		w=v.rot90()
		self.assertEqual(w.x,0)
		self.assertEqual(w.y,10)
	def testCompareLength(self):
		p1=Pt(0,0)
		p2=Pt(3,4)
		p3=Pt(5,12)
		len11=osmcmd.Length(p1-p1)
		len12=osmcmd.Length(p2-p1)
		len13=osmcmd.Length(p3-p1)
		self.assertTrue(len11<len13)
		self.assertTrue(len11<len12)
		self.assertTrue(len12<len13)
	# def testToLeft(self):
	# 	p1=Pt(0,0)
	# 	p2=Pt(0,10)
	# 	self.assertTrue(Pt(5,5).toLeftOfSegment(p1,p2))

class TestPoiAlign(unittest.TestCase):
	def testPullLine(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,3),
			[Pt(-10,0),Pt(10,0)],
			len
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(0,1))
	def testPushLine(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,1),
			[Pt(-10,0),Pt(10,0)],
			len
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(0,1))
	def testPullInsideAngle(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(4,3),
			[Pt(0,10),Pt(0,0),Pt(10,0)],
			len
		)
		self.assertAlmostEqual(npt.x,4)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,4)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(1,2))
	def testPushInsideAngle(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,1),
			[Pt(0,10),Pt(0,0),Pt(10,0)],
			len
		)
		self.assertAlmostEqual(npt.x,2)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(1,))
	def testPushInsideAngleSide(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,5),
			[Pt(0,10),Pt(0,0),Pt(10,0)],
			len
		)
		self.assertAlmostEqual(npt.x,2)
		self.assertAlmostEqual(npt.y,5)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,5)
		self.assertEqual(wpi,(0,1))
	def testPullOutsideAngle(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,50),
			[Pt(-10,0),Pt(0,20),Pt(20,0)],
			len
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,22)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,20)
		self.assertEqual(wpi,(1,))
	def testPushOutsideAngle(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,21),
			[Pt(-10,0),Pt(0,20),Pt(20,0)],
			len
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,22)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,20)
		self.assertEqual(wpi,(1,))
	def testPushBeak(self):
		pt=osmcmd.Point('latlon',60,30)
		len=osmcmd.Length(1,pt)
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,1),
			[Pt(0,10),Pt(0,1),Pt(-100,-100),Pt(1,0),Pt(10,0)],
			len
		)
		self.assertAlmostEqual(npt.x,2)
		self.assertAlmostEqual(npt.y,2)

if __name__=='__main__':
        unittest.main()
