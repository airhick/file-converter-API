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

## Deployment

### Local Deployment with Docker
```bash
docker build -t image-converter-api .
docker run -p 5000:5000 image-converter-api
```

### Deploying to Render

1. Create a Render account at [render.com](https://render.com)

2. Connect your GitHub repository to Render:
   - Go to the Render dashboard
   - Click "New" and select "Web Service"
   - Connect your GitHub repository

3. Configure the service:
   - **Name**: Choose a name for your service (e.g., image-converter-api)
   - **Environment**: Docker
   - **Branch**: main (or your preferred branch)
   - **Plan**: Free (or choose a paid plan for more resources)
   - **Advanced Settings**: Add any environment variables if needed

4. Click "Create Web Service"

Render will automatically build and deploy your application. The deployment process may take a few minutes.

#### Using render.yaml (Infrastructure as Code)

Alternatively, you can use the provided `render.yaml` file for deployment:

1. Push your code to GitHub
2. In Render dashboard, go to "Blueprints"
3. Connect your repository
4. Render will detect the `render.yaml` file and set up the services accordingly

## License

MIT
