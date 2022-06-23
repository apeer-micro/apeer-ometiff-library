import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import itertools as it
import numpy as np
from apeer_ometiff_library import io

class TestsCore(unittest.TestCase):

    def test_funcName_condition_expectedResult(self):
        pass

if __name__ == '__main__':
    unittest.main()