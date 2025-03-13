import os
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import logging

# Import the non-rawpy version of the converter
from app.services.converter_no_rawpy import ImageConverter
from app.utils.format_validator import is_valid_format, get_supported_output_formats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def index():
    """Serve a simple HTML form for testing the API"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Converter API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #333;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }
            form {
                background: #f9f9f9;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            select, input[type="file"], input[type="number"] {
                width: 100%;
                padding: 8px;
                margin-bottom: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #45a049;
            }
            .formats {
                margin-top: 30px;
            }
            code {
                background: #f5f5f5;
                padding: 2px 5px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <h1>Image Converter API</h1>
        <p>Use this form to test the image conversion API. The converted file will download automatically.</p>
        
        <form action="/convert" method="post" enctype="multipart/form-data">
            <div>
                <label for="image">Select Image:</label>
                <input type="file" id="image" name="image" required>
            </div>
            
            <div>
                <label for="target_format">Target Format:</label>
                <select id="target_format" name="target_format" required>
                    <option value="jpg">JPEG</option>
                    <option value="png">PNG</option>
                    <option value="webp">WebP</option>
                    <option value="gif">GIF</option>
                    <option value="tiff">TIFF</option>
                    <option value="bmp">BMP</option>
                    <option value="pdf">PDF</option>
                </select>
            </div>
            
            <div>
                <label for="quality">Quality (1-100):</label>
                <input type="number" id="quality" name="quality" min="1" max="100" value="90">
            </div>
            
            <button type="submit">Convert Image</button>
        </form>
        
        <div class="formats">
            <h2>API Documentation</h2>
            <p>For programmatic access, send a POST request to <code>/convert</code> with the following parameters:</p>
            <ul>
                <li><code>image</code>: The image file to convert</li>
                <li><code>target_format</code>: The desired output format (e.g., "png", "jpg", "webp")</li>
                <li><code>quality</code> (optional): For lossy formats, the quality level (1-100)</li>
            </ul>
            
            <h3>Example with cURL:</h3>
            <pre><code>curl -X POST -F "image=@/path/to/image.jpg" -F "target_format=png" -F "quality=90" https://file-converter-api-kn5c.onrender.com/convert -o converted_image.png</code></pre>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/advanced', methods=['GET'])
def advanced():
    """Serve the advanced HTML interface"""
    try:
        with open('app/templates/advanced.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Advanced template not found", 404

@app.route('/formats', methods=['GET'])
def get_formats():
    """Get all supported formats"""
    input_formats = list(get_supported_output_formats().keys())
    output_formats = {}
    
    for input_format in input_formats:
        output_formats[input_format] = get_supported_output_formats()[input_format]
    
    return jsonify({
        "input_formats": input_formats,
        "output_formats": output_formats
    }), 200

@app.route('/convert', methods=['POST'])
def convert_image():
    """Convert an image from one format to another"""
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files['image']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Get target format
    target_format = request.form.get('target_format')
    if not target_format:
        return jsonify({"error": "No target format specified"}), 400
    
    # Validate target format
    if not is_valid_format(target_format):
        return jsonify({"error": f"Unsupported target format: {target_format}"}), 400
    
    # Get quality parameter (optional)
    quality = request.form.get('quality', 90)
    try:
        quality = int(quality)
        if quality < 1 or quality > 100:
            raise ValueError("Quality must be between 1 and 100")
    except ValueError:
        return jsonify({"error": "Quality must be an integer between 1 and 100"}), 400
    
    # Save the uploaded file temporarily
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)
    
    try:
        # Create a temporary file for the output
        output_fd, output_path = tempfile.mkstemp(suffix=f'.{target_format}')
        os.close(output_fd)
        
        # Convert the image
        converter = ImageConverter()
        converter.convert(input_path, output_path, target_format, quality)
        
        # Generate a meaningful filename for the download
        output_filename = f"{os.path.splitext(filename)[0]}.{target_format}"
        
        # Get the MIME type for the target format
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'tiff': 'image/tiff',
            'bmp': 'image/bmp',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'eps': 'application/postscript'
        }
        mime_type = mime_types.get(target_format, 'application/octet-stream')
        
        # Send the converted file with headers optimized for download
        response = send_file(
            output_path,
            as_attachment=True,  # Force download rather than display in browser
            download_name=output_filename,
            mimetype=mime_type
        )
        
        # Add headers to encourage direct download
        response.headers["Content-Disposition"] = f"attachment; filename={output_filename}"
        response.headers["Content-Type"] = mime_type
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        return response
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500
    finally:
        # Clean up temporary files
        if os.path.exists(input_path):
            os.remove(input_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('app/static', path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 