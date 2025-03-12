import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import logging

from services.converter import ImageConverter
from utils.format_validator import is_valid_format, get_supported_output_formats

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
        
        # Send the converted file
        return send_file(output_path, 
                         as_attachment=True, 
                         download_name=f"{os.path.splitext(filename)[0]}.{target_format}")
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500
    finally:
        # Clean up temporary files
        if os.path.exists(input_path):
            os.remove(input_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 