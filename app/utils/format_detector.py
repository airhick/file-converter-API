"""
Format detector utility for the image conversion API.
Detects image formats from file content and extensions.
"""

import os
import magic
import logging
from PIL import Image
import imghdr

logger = logging.getLogger(__name__)

def detect_format_from_extension(filename):
    """
    Detect format from file extension.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        str: The detected format or None if not detected
    """
    if not filename:
        return None
    
    # Get the extension without the dot
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    # Common image extensions
    if ext in ['jpg', 'jpeg']:
        return 'jpg'
    elif ext == 'png':
        return 'png'
    elif ext == 'gif':
        return 'gif'
    elif ext == 'webp':
        return 'webp'
    elif ext in ['tif', 'tiff']:
        return 'tiff'
    elif ext == 'bmp':
        return 'bmp'
    elif ext == 'svg':
        return 'svg'
    elif ext in ['heif', 'heic']:
        return 'heif'
    elif ext in ['arw', 'cr2', 'nef', 'orf', 'rw2', 'dng']:
        return 'raw'
    elif ext == 'eps':
        return 'eps'
    elif ext == 'psd':
        return 'psd'
    elif ext == 'ai':
        return 'ai'
    elif ext == 'pdf':
        return 'pdf'
    elif ext == 'ico':
        return 'ico'
    elif ext == 'pcx':
        return 'pcx'
    elif ext == 'jxr':
        return 'jxr'
    elif ext == 'tga':
        return 'tga'
    elif ext == 'ppm':
        return 'ppm'
    elif ext == 'xcf':
        return 'xcf'
    elif ext == 'dxf':
        return 'dxf'
    
    return None

def detect_format_from_content(file_path):
    """
    Detect format from file content using multiple methods.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: The detected format or None if not detected
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    # Try using python-magic first
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        
        if 'jpeg' in mime_type:
            return 'jpg'
        elif 'png' in mime_type:
            return 'png'
        elif 'gif' in mime_type:
            return 'gif'
        elif 'webp' in mime_type:
            return 'webp'
        elif 'tiff' in mime_type:
            return 'tiff'
        elif 'bmp' in mime_type:
            return 'bmp'
        elif 'svg' in mime_type or 'xml' in mime_type:
            # Check if it's actually SVG
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 chars
                if '<svg' in content:
                    return 'svg'
        elif 'pdf' in mime_type:
            return 'pdf'
        elif 'postscript' in mime_type:
            return 'eps'
        elif 'photoshop' in mime_type or 'psd' in mime_type:
            return 'psd'
        elif 'illustrator' in mime_type:
            return 'ai'
        elif 'heif' in mime_type or 'heic' in mime_type:
            return 'heif'
        elif 'x-icon' in mime_type:
            return 'ico'
    except Exception as e:
        logger.warning(f"Error using python-magic: {str(e)}")
    
    # Try using imghdr
    try:
        img_type = imghdr.what(file_path)
        if img_type:
            if img_type == 'jpeg':
                return 'jpg'
            return img_type
    except Exception as e:
        logger.warning(f"Error using imghdr: {str(e)}")
    
    # Try using PIL
    try:
        with Image.open(file_path) as img:
            fmt = img.format.lower()
            if fmt == 'jpeg':
                return 'jpg'
            return fmt
    except Exception as e:
        logger.warning(f"Error using PIL: {str(e)}")
    
    # Fall back to extension
    return detect_format_from_extension(file_path)

def detect_format(file_path):
    """
    Detect format from file content and extension.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: The detected format or None if not detected
    """
    # Try content detection first
    format_from_content = detect_format_from_content(file_path)
    if format_from_content:
        return format_from_content
    
    # Fall back to extension
    return detect_format_from_extension(file_path) 