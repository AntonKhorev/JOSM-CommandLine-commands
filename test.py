import unittest
import osmcmd

class TestOsmCommandline(unittest.TestCase):
	def testNodeDistance(self):
		p1=osmcmd.Point('latlon',59.929928003648804,30.39256987360226)
		p2=osmcmd.Point('latlon',59.93093128613418,30.397014125548477)
		len=osmcmd.Length(20,p1)
		pr=p1+(p2-p1).unit()*len
		self.assertAlmostEqual(pr.lat,59.9300018058)
		self.assertAlmostEqual(pr.lon,30.3928967912)

if __name__=='__main__':
        unittest.main()
