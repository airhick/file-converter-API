"""
Image converter service for the image conversion API.
Handles conversion between different image formats.
"""

import os
import logging
import tempfile
import subprocess
from PIL import Image
import cairosvg
from wand.image import Image as WandImage
from pdf2image import convert_from_path
import rawpy
import numpy as np

from app.utils.format_detector import detect_format
from app.utils.format_validator import get_normalized_format, can_convert

logger = logging.getLogger(__name__)

class ImageConverter:
    """
    Image converter class that handles conversion between different formats.
    Uses different libraries depending on the input and output formats.
    """
    
    def __init__(self):
        """Initialize the converter."""
        pass
    
    def convert(self, input_path, output_path, target_format, quality=90):
        """
        Convert an image from one format to another.
        
        Args:
            input_path (str): Path to the input image
            output_path (str): Path to save the output image
            target_format (str): Target format to convert to
            quality (int, optional): Quality for lossy formats (1-100). Defaults to 90.
            
        Returns:
            bool: True if conversion was successful, False otherwise
            
        Raises:
            ValueError: If conversion is not supported
            FileNotFoundError: If input file does not exist
            Exception: For other errors during conversion
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Detect input format
        input_format = detect_format(input_path)
        if not input_format:
            raise ValueError(f"Could not detect format of input file: {input_path}")
        
        # Normalize formats
        input_format = get_normalized_format(input_format)
        target_format = get_normalized_format(target_format)
        
        if not target_format:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        # Check if conversion is supported
        if not can_convert(input_format, target_format):
            raise ValueError(f"Conversion from {input_format} to {target_format} is not supported")
        
        logger.info(f"Converting {input_path} from {input_format} to {target_format}")
        
        # Choose the appropriate conversion method
        try:
            if input_format in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'tiff', 'bmp']:
                return self._convert_standard(input_path, output_path, target_format, quality)
            elif input_format == 'svg':
                return self._convert_svg(input_path, output_path, target_format, quality)
            elif input_format in ['heif', 'heic']:
                return self._convert_heif(input_path, output_path, target_format, quality)
            elif input_format == 'raw' or input_format in ['arw', 'cr2', 'nef', 'orf', 'rw2', 'dng']:
                return self._convert_raw(input_path, output_path, target_format, quality)
            elif input_format in ['eps', 'ai']:
                return self._convert_eps_ai(input_path, output_path, target_format, quality)
            elif input_format == 'psd':
                return self._convert_psd(input_path, output_path, target_format, quality)
            elif input_format == 'pdf':
                return self._convert_pdf(input_path, output_path, target_format, quality)
            elif input_format == 'ico':
                return self._convert_ico(input_path, output_path, target_format, quality)
            elif input_format in ['pcx', 'jxr', 'tga', 'ppm', 'xcf', 'dxf']:
                return self._convert_specialized(input_path, output_path, target_format, quality)
            else:
                raise ValueError(f"Unsupported input format: {input_format}")
        except Exception as e:
            logger.error(f"Error during conversion: {str(e)}")
            raise
    
    def _convert_standard(self, input_path, output_path, target_format, quality):
        """Convert standard image formats using PIL."""
        with Image.open(input_path) as img:
            # Convert to RGB if saving as JPEG (JPEG doesn't support alpha)
            if target_format in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA']:
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            
            # Save with appropriate options
            save_kwargs = {}
            if target_format in ['jpg', 'jpeg']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            elif target_format == 'png':
                save_kwargs['optimize'] = True
            elif target_format == 'webp':
                save_kwargs['quality'] = quality
                save_kwargs['method'] = 6  # Higher quality but slower
            elif target_format == 'tiff':
                save_kwargs['compression'] = 'tiff_lzw'
            
            # Map format names to PIL format names
            format_map = {
                'jpg': 'JPEG',
                'jpeg': 'JPEG',
                'png': 'PNG',
                'gif': 'GIF',
                'webp': 'WEBP',
                'tiff': 'TIFF',
                'bmp': 'BMP'
            }
            
            img.save(output_path, format=format_map[target_format], **save_kwargs)
        
        return True
    
    def _convert_svg(self, input_path, output_path, target_format, quality):
        """Convert SVG to other formats."""
        if target_format == 'pdf':
            cairosvg.svg2pdf(url=input_path, write_to=output_path)
        elif target_format in ['png', 'jpg', 'jpeg']:
            # For raster formats, use cairosvg
            if target_format == 'png':
                cairosvg.svg2png(url=input_path, write_to=output_path)
            else:  # jpg/jpeg
                # Convert to PNG first, then to JPEG
                temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
                try:
                    cairosvg.svg2png(url=input_path, write_to=temp_png)
                    with Image.open(temp_png) as img:
                        img = img.convert('RGB')  # Remove alpha for JPEG
                        img.save(output_path, 'JPEG', quality=quality, optimize=True)
                finally:
                    if os.path.exists(temp_png):
                        os.remove(temp_png)
        elif target_format in ['gif', 'webp', 'tiff']:
            # Convert to PNG first, then to target format
            temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
            try:
                cairosvg.svg2png(url=input_path, write_to=temp_png)
                self._convert_standard(temp_png, output_path, target_format, quality)
            finally:
                if os.path.exists(temp_png):
                    os.remove(temp_png)
        else:
            raise ValueError(f"Conversion from SVG to {target_format} is not implemented")
        
        return True
    
    def _convert_heif(self, input_path, output_path, target_format, quality):
        """Convert HEIF/HEIC to other formats."""
        # Use Pillow with the pillow-heif plugin if available
        try:
            with Image.open(input_path) as img:
                return self._convert_standard(input_path, output_path, target_format, quality)
        except Exception as e:
            logger.warning(f"Error using Pillow for HEIF: {str(e)}")
        
        # Fallback to using external tools
        try:
            # Convert to PNG first using heif-convert
            temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
            try:
                subprocess.run(['heif-convert', input_path, temp_png], check=True)
                return self._convert_standard(temp_png, output_path, target_format, quality)
            finally:
                if os.path.exists(temp_png):
                    os.remove(temp_png)
        except Exception as e:
            logger.error(f"Error converting HEIF: {str(e)}")
            raise ValueError(f"Failed to convert HEIF: {str(e)}")
    
    def _convert_raw(self, input_path, output_path, target_format, quality):
        """Convert RAW camera formats to other formats."""
        try:
            with rawpy.imread(input_path) as raw:
                # Process the raw data
                rgb = raw.postprocess(use_camera_wb=True, half_size=False, no_auto_bright=False)
                
                # Convert to PIL Image
                img = Image.fromarray(rgb)
                
                # Save to temporary file
                temp_tiff = tempfile.NamedTemporaryFile(suffix='.tiff', delete=False).name
                img.save(temp_tiff)
                
                # Convert from TIFF to target format
                return self._convert_standard(temp_tiff, output_path, target_format, quality)
        except Exception as e:
            logger.error(f"Error converting RAW: {str(e)}")
            raise ValueError(f"Failed to convert RAW: {str(e)}")
    
    def _convert_eps_ai(self, input_path, output_path, target_format, quality):
        """Convert EPS/AI to other formats."""
        try:
            with WandImage(filename=input_path) as img:
                # For vector output formats
                if target_format in ['svg', 'pdf', 'eps']:
                    img.format = target_format.upper()
                    img.save(filename=output_path)
                # For raster output formats
                else:
                    # Set resolution for raster conversion
                    img.resolution = (300, 300)
                    
                    # Convert to PNG first for better quality
                    temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
                    try:
                        img.format = 'PNG'
                        img.save(filename=temp_png)
                        
                        # Convert from PNG to target format
                        return self._convert_standard(temp_png, output_path, target_format, quality)
                    finally:
                        if os.path.exists(temp_png):
                            os.remove(temp_png)
            return True
        except Exception as e:
            logger.error(f"Error converting EPS/AI: {str(e)}")
            
            # Fallback to Ghostscript for EPS/AI
            try:
                # Convert to PDF first
                temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
                try:
                    subprocess.run(['gs', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', 
                                   f'-sOutputFile={temp_pdf}', input_path], check=True)
                    
                    # Convert from PDF to target format
                    return self._convert_pdf(temp_pdf, output_path, target_format, quality)
                finally:
                    if os.path.exists(temp_pdf):
                        os.remove(temp_pdf)
            except Exception as e2:
                logger.error(f"Error in Ghostscript fallback: {str(e2)}")
                raise ValueError(f"Failed to convert EPS/AI: {str(e)}, fallback failed: {str(e2)}")
    
    def _convert_psd(self, input_path, output_path, target_format, quality):
        """Convert PSD to other formats."""
        try:
            # Try using Pillow first
            with Image.open(input_path) as img:
                return self._convert_standard(input_path, output_path, target_format, quality)
        except Exception as e:
            logger.warning(f"Error using Pillow for PSD: {str(e)}")
        
        # Fallback to using Wand/ImageMagick
        try:
            with WandImage(filename=input_path) as img:
                # Set format and save
                if target_format in ['jpg', 'jpeg']:
                    img.format = 'JPEG'
                    img.compression_quality = quality
                else:
                    img.format = target_format.upper()
                
                img.save(filename=output_path)
            return True
        except Exception as e:
            logger.error(f"Error converting PSD: {str(e)}")
            raise ValueError(f"Failed to convert PSD: {str(e)}")
    
    def _convert_pdf(self, input_path, output_path, target_format, quality):
        """Convert PDF to other formats."""
        # For vector output formats
        if target_format in ['svg']:
            try:
                # Use pdf2svg
                subprocess.run(['pdf2svg', input_path, output_path, '1'], check=True)
                return True
            except Exception as e:
                logger.error(f"Error converting PDF to SVG: {str(e)}")
                raise ValueError(f"Failed to convert PDF to SVG: {str(e)}")
        
        # For raster output formats
        try:
            # Convert first page of PDF to image
            images = convert_from_path(input_path, first_page=1, last_page=1)
            if not images:
                raise ValueError("Failed to convert PDF: No images extracted")
            
            # Save the first page
            img = images[0]
            
            # For JPEG, convert to RGB
            if target_format in ['jpg', 'jpeg']:
                img = img.convert('RGB')
            
            # Save with appropriate options
            save_kwargs = {}
            if target_format in ['jpg', 'jpeg']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            
            # Map format names to PIL format names
            format_map = {
                'jpg': 'JPEG',
                'jpeg': 'JPEG',
                'png': 'PNG',
                'gif': 'GIF',
                'webp': 'WEBP',
                'tiff': 'TIFF'
            }
            
            img.save(output_path, format=format_map.get(target_format, target_format.upper()), **save_kwargs)
            return True
        except Exception as e:
            logger.error(f"Error converting PDF: {str(e)}")
            raise ValueError(f"Failed to convert PDF: {str(e)}")
    
    def _convert_ico(self, input_path, output_path, target_format, quality):
        """Convert ICO to other formats."""
        try:
            with Image.open(input_path) as img:
                return self._convert_standard(input_path, output_path, target_format, quality)
        except Exception as e:
            logger.warning(f"Error using Pillow for ICO: {str(e)}")
            
            # Fallback to using Wand/ImageMagick
            try:
                with WandImage(filename=input_path) as img:
                    if target_format in ['jpg', 'jpeg']:
                        img.format = 'JPEG'
                        img.compression_quality = quality
                    else:
                        img.format = target_format.upper()
                    
                    img.save(filename=output_path)
                return True
            except Exception as e2:
                logger.error(f"Error converting ICO: {str(e2)}")
                raise ValueError(f"Failed to convert ICO: {str(e2)}")
    
    def _convert_specialized(self, input_path, output_path, target_format, quality):
        """Convert specialized formats (PCX, JXR, TGA, PPM, XCF, DXF)."""
        # Try using Pillow first for formats it supports
        try:
            with Image.open(input_path) as img:
                return self._convert_standard(input_path, output_path, target_format, quality)
        except Exception as e:
            logger.warning(f"Error using Pillow for specialized format: {str(e)}")
        
        # Fallback to using Wand/ImageMagick
        try:
            with WandImage(filename=input_path) as img:
                if target_format in ['jpg', 'jpeg']:
                    img.format = 'JPEG'
                    img.compression_quality = quality
                else:
                    img.format = target_format.upper()
                
                img.save(filename=output_path)
            return True
        except Exception as e:
            logger.error(f"Error converting specialized format: {str(e)}")
            
            # For DXF specifically, try using dxf2svg and then convert from SVG
            if input_path.lower().endswith('.dxf'):
                try:
                    # Convert DXF to SVG first
                    temp_svg = tempfile.NamedTemporaryFile(suffix='.svg', delete=False).name
                    try:
                        subprocess.run(['dxf2svg', input_path, '-o', temp_svg], check=True)
                        return self._convert_svg(temp_svg, output_path, target_format, quality)
                    finally:
                        if os.path.exists(temp_svg):
                            os.remove(temp_svg)
                except Exception as e2:
                    logger.error(f"Error in DXF conversion fallback: {str(e2)}")
            
            raise ValueError(f"Failed to convert specialized format: {str(e)}") 