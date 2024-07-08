import unittest
from config import Config
import os
from dotenv import load_dotenv

class TestConfig(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()

    def test_config_values(self):
        self.assertEqual(Config.MAX_DEPTH, int(os.getenv('MAX_DEPTH', 10)))
        self.assertEqual(Config.BASE_THICKNESS, int(os.getenv('BASE_THICKNESS', 4)))
        self.assertEqual(Config.OUTPUT_WIDTH, int(os.getenv('OUTPUT_WIDTH', 200)))
        self.assertEqual(Config.RESOLUTION, float(os.getenv('RESOLUTION', 0.5)))
        self.assertEqual(Config.SMOOTHNESS, int(os.getenv('SMOOTHNESS', 1)))
        self.assertEqual(Config.GRAY_SCALE, os.getenv('GRAY_SCALE', 'True').lower() == 'true')
        self.assertEqual(Config.TOP_SURFACE_SMOOTHNESS, int(os.getenv('TOP_SURFACE_SMOOTHNESS', 9)))
        self.assertEqual(Config.INVERT, os.getenv('INVERT', 'False').lower() == 'true')

if __name__ == '__main__':
    unittest.main()
