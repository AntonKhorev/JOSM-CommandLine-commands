import unittest
import osmcmd
import poialign

def Pt(x,y):
	return osmcmd.Point('xy',x,y)

class TestOsmCommandline(unittest.TestCase):
	def testNodeDistance(self):
		p1=osmcmd.Point('latlon',59.929928003648804,30.39256987360226)
		p2=osmcmd.Point('latlon',59.93093128613418,30.397014125548477)
		len=osmcmd.Length(20,p1)
		pr=p1+(p2-p1).dir()*len
		self.assertAlmostEqual(pr.lat,59.9300018058)
		self.assertAlmostEqual(pr.lon,30.3928967912)

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
	def testPullAngle(self):
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
	def testPushAngle(self):
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

if __name__=='__main__':
        unittest.main()
