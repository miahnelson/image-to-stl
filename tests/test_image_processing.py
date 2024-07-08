import unittest
import os
from image_processing import LithophaneCreator
import numpy as np
from stl import mesh
import cv2

class TestLithophaneCreator(unittest.TestCase):

    def setUp(self):
        self.processor = LithophaneCreator(
            max_depth=10,
            base_thickness=4,
            output_width=200,
            invert=True,
            resolution=0.5,
            smoothness=1,
            grayscale=True,
            top_surface_smoothness=9
        )
        self.test_image_path = 'test_image.jpg'
        self.output_stl_path = 'test_output.stl'
        self.fixed_output_stl_path = 'test_output_fixed.stl'

        # Create a test image
        self.test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        self.test_image = cv2.putText(self.test_image, 'Test', (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.imwrite(self.test_image_path, self.test_image)

    def tearDown(self):
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.output_stl_path):
            os.remove(self.output_stl_path)
        if os.path.exists(self.fixed_output_stl_path):
            os.remove(self.fixed_output_stl_path)

    def test_create_lithophane(self):
        fixed_output_path = self.processor.create_lithophane(self.test_image_path, self.output_stl_path)
        self.assertTrue(os.path.exists(self.output_stl_path))
        self.assertTrue(os.path.exists(fixed_output_path))
        
        # Load the STL file and check if it contains vertices
        stl_mesh = mesh.Mesh.from_file(fixed_output_path)
        self.assertGreater(len(stl_mesh.points), 0)

if __name__ == '__main__':
    unittest.main()
