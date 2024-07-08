import unittest
import os
import json
from app import app
import cv2
import numpy as np

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'test_uploads'
        app.config['OUTPUT_FOLDER'] = 'test_outputs'
        self.client = app.test_client()

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        if not os.path.exists(app.config['OUTPUT_FOLDER']):
            os.makedirs(app.config['OUTPUT_FOLDER'])

        # Create a test image
        self.test_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_image.jpg')
        self.test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        self.test_image = cv2.putText(self.test_image, 'Test', (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.imwrite(self.test_image_path, self.test_image)

    def tearDown(self):
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
            os.rmdir(app.config['UPLOAD_FOLDER'])

        if os.path.exists(app.config['OUTPUT_FOLDER']):
            for f in os.listdir(app.config['OUTPUT_FOLDER']):
                os.remove(os.path.join(app.config['OUTPUT_FOLDER'], f))
            os.rmdir(app.config['OUTPUT_FOLDER'])

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Image to STL Converter', response.data)

    def test_upload_and_process_image(self):
        with open(self.test_image_path, 'rb') as img:
            data = {
                'file': (img, 'test_image.jpg'),
                'max_depth': 10,
                'base_thickness': 4,
                'output_width': 200,
                'invert': 'false',
                'resolution': 0.5,
                'smoothness': 1,
                'grayscale': 'true',
                'top_surface_smoothness': 9
            }
            response = self.client.post('/', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        self.assertIn('stl_url', response_data)

    def test_download_file(self):
        # Create a test output file
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'test_output_fixed.stl')
        with open(output_path, 'w') as f:
            f.write('test')

        response = self.client.get('/download/test_output_fixed.stl')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename=test_output_fixed.stl')

if __name__ == '__main__':
    unittest.main()
