# Image Conversion API

A RESTful API for converting images between various formats.

## Supported Formats

### Input Formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- TIFF (.tif, .tiff)
- BMP (.bmp)
- SVG (.svg)
- HEIF (.heif, .heic)
- RAW (Digital Camera Format)
- EPS (.eps)
- PSD (Photoshop)
- AI (Adobe Illustrator)
- PDF (.pdf)
- ICO (.ico)
- PCX (.pcx)
- JXR (.jxr)
- TGA (.tga)
- PPM (.ppm)
- XCF (GIMP)
- DXF (.dxf)

### Output Formats:
Depending on the input format, the API can convert to various formats including:
- JPEG
- PNG
- GIF
- WebP
- TIFF
- BMP
- SVG
- PDF
- EPS

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install system dependencies:
   - For SVG support: Cairo graphics library
   - For PDF support: Poppler
   - For RAW support: LibRaw
   - For AI/EPS support: Ghostscript
   - For HEIF support: libheif

## Usage

1. Start the server:
   ```
   python app/app.py
   ```

2. Make a POST request to `/convert` with:
   - An image file
   - Target format parameter

Example using curl:
```
curl -X POST -F "image=@path/to/image.jpg" -F "target_format=png" http://localhost:5000/convert
```

## API Endpoints

### POST /convert
Converts an uploaded image to the specified format.

**Parameters:**
- `image`: The image file to convert
- `target_format`: The desired output format (e.g., "png", "jpg", "webp")
- `quality` (optional): For lossy formats, the quality level (1-100)

**Response:**
- The converted image file

## License

MIT # file-converter-API
