import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine.sampling_preferences import adaptive,uniform

class TestSampling(unittest.TestCase):
    def test_uniform(self):
        v=uniform(lambda t:(t,t*t),-1,1,1001)
        self.assertEqual(len(v.parametros),1001)
        self.assertAlmostEqual(v.parametros[500],0)
    def test_adaptive(self):
        v=adaptive(lambda t:(t,t*t),-1,1,.001,.5,1000)
        self.assertGreater(len(v.parametros),3)
        self.assertAlmostEqual(v.parametros[0],-1)
        self.assertAlmostEqual(v.parametros[-1],1)
    def test_invalid(self):
        with self.assertRaises(ValueError):
            adaptive(lambda t:(t,t),1,-1,.001,.5)
if __name__=='__main__':unittest.main()
