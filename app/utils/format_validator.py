"""
Format validator utility for the image conversion API.
Defines supported input and output formats and validation functions.
"""

# Define supported formats and their valid output formats
SUPPORTED_FORMATS = {
    # Standard web formats
    'jpg': ['png', 'gif', 'webp', 'tiff', 'bmp'],
    'jpeg': ['png', 'gif', 'webp', 'tiff', 'bmp'],
    'png': ['jpg', 'jpeg', 'gif', 'webp', 'tiff', 'bmp'],
    'gif': ['png', 'jpg', 'jpeg', 'webp', 'tiff'],
    'webp': ['png', 'jpg', 'jpeg', 'gif', 'tiff'],
    'tiff': ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'],
    'tif': ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'],
    'bmp': ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'webp'],
    
    # Vector formats
    'svg': ['png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'],
    
    # High-efficiency formats
    'heif': ['jpg', 'jpeg', 'png', 'webp', 'tiff', 'gif'],
    'heic': ['jpg', 'jpeg', 'png', 'webp', 'tiff', 'gif'],
    
    # Camera RAW formats (generalized as 'raw')
    'raw': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],
    'arw': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],  # Sony
    'cr2': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],  # Canon
    'nef': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],  # Nikon
    'orf': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],  # Olympus
    'rw2': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],  # Panasonic
    'dng': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],  # Adobe
    
    # Adobe formats
    'eps': ['jpg', 'jpeg', 'png', 'svg', 'pdf', 'tiff'],
    'psd': ['jpg', 'jpeg', 'png', 'tiff', 'gif', 'webp'],
    'ai': ['jpg', 'jpeg', 'png', 'svg', 'eps', 'pdf'],
    
    # Document format
    'pdf': ['jpg', 'jpeg', 'png', 'tiff', 'gif', 'svg'],
    
    # Other formats
    'ico': ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'],
    'pcx': ['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif'],
    'jxr': ['jpg', 'jpeg', 'png', 'webp', 'tiff'],
    'tga': ['jpg', 'jpeg', 'png', 'tiff', 'gif'],
    'ppm': ['png', 'jpg', 'jpeg', 'tiff', 'bmp'],
    'xcf': ['jpg', 'jpeg', 'png', 'tiff', 'gif', 'webp'],
    'dxf': ['png', 'jpg', 'jpeg', 'svg', 'pdf', 'tiff'],
}

# File extensions mapping (for detection)
FILE_EXTENSIONS = {
    # Standard web formats
    'jpg': ['jpg', 'jpeg'],
    'jpeg': ['jpg', 'jpeg'],
    'png': ['png'],
    'gif': ['gif'],
    'webp': ['webp'],
    'tiff': ['tiff', 'tif'],
    'tif': ['tiff', 'tif'],
    'bmp': ['bmp'],
    
    # Vector formats
    'svg': ['svg'],
    
    # High-efficiency formats
    'heif': ['heif', 'heic'],
    'heic': ['heif', 'heic'],
    
    # Camera RAW formats
    'raw': ['raw', 'arw', 'cr2', 'nef', 'orf', 'rw2', 'dng'],
    
    # Adobe formats
    'eps': ['eps'],
    'psd': ['psd'],
    'ai': ['ai'],
    
    # Document format
    'pdf': ['pdf'],
    
    # Other formats
    'ico': ['ico'],
    'pcx': ['pcx'],
    'jxr': ['jxr'],
    'tga': ['tga'],
    'ppm': ['ppm'],
    'xcf': ['xcf'],
    'dxf': ['dxf'],
}

def is_valid_format(format_name):
    """
    Check if a format is supported for output.
    
    Args:
        format_name (str): The format name to check
        
    Returns:
        bool: True if the format is supported, False otherwise
    """
    format_name = format_name.lower()
    
    # Check if it's a direct format
    if format_name in SUPPORTED_FORMATS:
        return True
    
    # Check if it's an alias (extension)
    for fmt, extensions in FILE_EXTENSIONS.items():
        if format_name in extensions:
            return True
    
    return False

def get_normalized_format(format_name):
    """
    Get the normalized format name from any valid format name or extension.
    
    Args:
        format_name (str): The format name or extension
        
    Returns:
        str: The normalized format name
    """
    format_name = format_name.lower()
    
    # If it's already a supported format
    if format_name in SUPPORTED_FORMATS:
        return format_name
    
    # Check if it's an extension
    for fmt, extensions in FILE_EXTENSIONS.items():
        if format_name in extensions:
            return fmt
    
    return None

def get_supported_output_formats(input_format=None):
    """
    Get all supported output formats for a given input format.
    If no input format is provided, returns all supported formats.
    
    Args:
        input_format (str, optional): The input format
        
    Returns:
        dict: Dictionary of supported output formats
    """
    if input_format:
        normalized_format = get_normalized_format(input_format)
        if normalized_format:
            return {normalized_format: SUPPORTED_FORMATS[normalized_format]}
        return {}
    
    return SUPPORTED_FORMATS

def can_convert(input_format, output_format):
    """
    Check if conversion from input_format to output_format is supported.
    
    Args:
        input_format (str): The input format
        output_format (str): The desired output format
        
    Returns:
        bool: True if conversion is supported, False otherwise
    """
    input_normalized = get_normalized_format(input_format)
    output_normalized = get_normalized_format(output_format)
    
    if not input_normalized or not output_normalized:
        return False
    
    return output_normalized in SUPPORTED_FORMATS.get(input_normalized, []) 