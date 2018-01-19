import unittest
import math
import osmcmd
import poialign

Pt=osmcmd.Point

class TestOsmCmd(unittest.TestCase):
	def testNodeDistance(self):
		p1=osmcmd.Point.fromLatLon(59.929928003648804,30.39256987360226)
		p2=osmcmd.Point.fromLatLon(59.93093128613418,30.397014125548477)
		len=p1.lengthFromMeters(20)
		pr=p1+(p2-p1).dir(len)
		self.assertAlmostEqual(pr.lat,59.9300018058)
		self.assertAlmostEqual(pr.lon,30.3928967912)
	def testVectorLength(self):
		p1=Pt(0,0)
		p2=Pt(3,4)
		len=(p2-p1).length
		self.assertAlmostEqual(len,5)
	def testVectorRot90(self):
		v=osmcmd.Vector(10,0)
		w=v.rot90()
		self.assertEqual(w.x,0)
		self.assertEqual(w.y,10)
	def testCompareLength(self):
		p1=Pt(0,0)
		p2=Pt(3,4)
		p3=Pt(5,12)
		len11=(p1-p1).length
		len12=(p2-p1).length
		len13=(p3-p1).length
		self.assertTrue(len11<len13)
		self.assertTrue(len11<len12)
		self.assertTrue(len12<len13)
	# def testToLeft(self):
	# 	p1=Pt(0,0)
	# 	p2=Pt(0,10)
	# 	self.assertTrue(Pt(5,5).toLeftOfSegment(p1,p2))
	def testSegment0(self):
		s1=osmcmd.Segment(Pt(0,0),Pt(0,1))
		s2=osmcmd.Segment(Pt(0,0),Pt(1,0))
		d1,d2=s1.intersect(s2)
		self.assertAlmostEqual(d1,0)
		self.assertAlmostEqual(d2,0)
	def testSegment1(self):
		s1=osmcmd.Segment(Pt(0,1),Pt(1,1))
		s2=osmcmd.Segment(Pt(1,0),Pt(1,1))
		d1,d2=s1.intersect(s2)
		self.assertAlmostEqual(d1,1)
		self.assertAlmostEqual(d2,1)
	def testSegmentX(self):
		s1=osmcmd.Segment(Pt(0,0),Pt(2,2))
		s2=osmcmd.Segment(Pt(1,0),Pt(0,1))
		d1,d2=s1.intersect(s2)
		self.assertAlmostEqual(d1,0.25)
		self.assertAlmostEqual(d2,0.5)

class TestPoiAlign(unittest.TestCase):
	def testPullLine(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,3),
			[Pt(-10,0),Pt(10,0)],
			2
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(0,1))
	def testPushLine(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,1),
			[Pt(-10,0),Pt(10,0)],
			2
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(0,1))
	def testPullInsideAngle(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(4,3),
			[Pt(0,10),Pt(0,0),Pt(10,0)],
			2
		)
		self.assertAlmostEqual(npt.x,4)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,4)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(1,2))
	def testPushInsideAngle(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,1),
			[Pt(0,10),Pt(0,0),Pt(10,0)],
			2
		)
		self.assertAlmostEqual(npt.x,2)
		self.assertAlmostEqual(npt.y,2)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,0)
		self.assertEqual(wpi,(1,))
	def testPushInsideAngleSide(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,5),
			[Pt(0,10),Pt(0,0),Pt(10,0)],
			2
		)
		self.assertAlmostEqual(npt.x,2)
		self.assertAlmostEqual(npt.y,5)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,5)
		self.assertEqual(wpi,(0,1))
	def testPullOutsideAngle(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,50),
			[Pt(-10,0),Pt(0,20),Pt(20,0)],
			2
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,22)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,20)
		self.assertEqual(wpi,(1,))
	def testPushOutsideAngle(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(0,21),
			[Pt(-10,0),Pt(0,20),Pt(20,0)],
			2
		)
		self.assertAlmostEqual(npt.x,0)
		self.assertAlmostEqual(npt.y,22)
		self.assertAlmostEqual(wpt.x,0)
		self.assertAlmostEqual(wpt.y,20)
		self.assertEqual(wpi,(1,))
	def testPushBeak(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,1),
			[Pt(0,10),Pt(0,1),Pt(-100,-100),Pt(1,0),Pt(10,0)],
			2
		)
		self.assertAlmostEqual(npt.x,2)
		self.assertAlmostEqual(npt.y,2)
	def testPushInsideAcuteAngle1(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,0),
			[Pt(10,5),Pt(0,0),Pt(10,-5)],
			math.sqrt(5)
		)
		self.assertAlmostEqual(npt.x,5,places=3)
		self.assertAlmostEqual(npt.y,0,places=3)
		self.assertAlmostEqual(wpt.x,0,places=3)
		self.assertAlmostEqual(wpt.y,0,places=3)
		self.assertEqual(wpi,(1,))
	def testPushInsideAcuteAngle2(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(2,0),
			[Pt(10,5),Pt(0,0),Pt(10,-5)],
			math.sqrt(5)
		)
		self.assertAlmostEqual(npt.x,5,places=3)
		self.assertAlmostEqual(npt.y,0,places=3)
		self.assertAlmostEqual(wpt.x,0,places=3)
		self.assertAlmostEqual(wpt.y,0,places=3)
		self.assertEqual(wpi,(1,))
	def testPushInsideBluntAngle(self):
		npt,wpt,wpi=poialign.getPoiAndEntranceLocations(
			Pt(1,0),
			[Pt(10,50),Pt(0,0),Pt(10,-50)],
			10
		)
		self.assertGreater(npt.x,10)
		self.assertAlmostEqual(npt.y,0,places=3)
		self.assertAlmostEqual(wpt.x,0,places=3)
		self.assertAlmostEqual(wpt.y,0,places=3)
		self.assertEqual(wpi,(1,))

if __name__=='__main__':
        unittest.main()
