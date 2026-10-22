import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location("model", Path(__file__).parents[1] / "scripts/verify-cache-model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
class CacheModelTests(unittest.TestCase):
    def test_known_vectors(self):
        for addresses, expected in [([], (0,0,0)), ([0], (0,1,0)), ([0,0], (1,1,0)), ([0,15,16,64,79,0,31,80], (3,5,3)), ([0,16,32,48,1,17,33,49,64,80,96,112,0,16,32,48], (4,12,8))]:
            self.assertEqual(model.simulate(addresses), expected)
    def test_locality(self):
        for n, column, expected in [(16,False,(240,16,12)), (16,True,(0,256,252)), (8,False,(60,4,0)), (8,True,(60,4,0))]:
            self.assertEqual(model.simulate(model.matrix(n,column)), expected)
if __name__ == "__main__": unittest.main()
