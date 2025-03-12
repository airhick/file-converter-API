"""
Tests for the image converter service.
"""

import os
import unittest
import tempfile
from PIL import Image

import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.converter import ImageConverter
from utils.format_validator import can_convert, get_normalized_format

class TestConverter(unittest.TestCase):
    """Test cases for the image converter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = ImageConverter()
        
        # Create a test image
        self.test_image_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_image_path)
    
    def tearDown(self):
        """Tear down test fixtures."""
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    def test_convert_png_to_jpg(self):
        """Test converting PNG to JPEG."""
        output_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False).name
        try:
            # Perform conversion
            result = self.converter.convert(self.test_image_path, output_path, 'jpg')
            
            # Check if conversion was successful
            self.assertTrue(result)
            self.assertTrue(os.path.exists(output_path))
            
            # Check if the output is a valid JPEG
            with Image.open(output_path) as img:
                self.assertEqual(img.format, 'JPEG')
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_convert_png_to_webp(self):
        """Test converting PNG to WebP."""
        output_path = tempfile.NamedTemporaryFile(suffix='.webp', delete=False).name
        try:
            # Perform conversion
            result = self.converter.convert(self.test_image_path, output_path, 'webp')
            
            # Check if conversion was successful
            self.assertTrue(result)
            self.assertTrue(os.path.exists(output_path))
            
            # Check if the output is a valid WebP
            with Image.open(output_path) as img:
                self.assertEqual(img.format, 'WEBP')
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_format_validation(self):
        """Test format validation functions."""
        # Test can_convert function
        self.assertTrue(can_convert('png', 'jpg'))
        self.assertTrue(can_convert('jpg', 'png'))
        self.assertTrue(can_convert('png', 'webp'))
        
        # Test normalization
        self.assertEqual(get_normalized_format('jpg'), 'jpg')
        self.assertEqual(get_normalized_format('jpeg'), 'jpeg')
        self.assertEqual(get_normalized_format('png'), 'png')

if __name__ == '__main__':
    unittest.main() 