/**
 * Image Converter API Client
 * 
 * This script demonstrates how to use the Image Converter API
 * and handle file downloads programmatically.
 */

/**
 * Convert an image using the API and trigger a download
 * @param {File} imageFile - The image file to convert
 * @param {string} targetFormat - The format to convert to (e.g., 'png', 'jpg')
 * @param {number} quality - Quality level for lossy formats (1-100)
 * @returns {Promise<void>}
 */
async function convertImage(imageFile, targetFormat, quality = 90) {
    // Create form data
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('target_format', targetFormat);
    formData.append('quality', quality);
    
    try {
        // Make the API request
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            // Handle error responses
            const errorData = await response.json();
            throw new Error(errorData.error || 'Conversion failed');
        }
        
        // Get the filename from the Content-Disposition header if available
        let filename = `converted.${targetFormat}`;
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1];
            }
        }
        
        // Convert the response to a blob
        const blob = await response.blob();
        
        // Create a download link and trigger the download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return { success: true, filename };
    } catch (error) {
        console.error('Error converting image:', error);
        throw error;
    }
}

/**
 * Example usage in a web application
 */
document.addEventListener('DOMContentLoaded', () => {
    // Find the form if it exists on the page
    const form = document.getElementById('converter-form');
    if (!form) return;
    
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const imageInput = document.getElementById('image');
        const targetFormatSelect = document.getElementById('target_format');
        const qualityInput = document.getElementById('quality');
        const resultDiv = document.getElementById('result');
        
        if (!imageInput.files || imageInput.files.length === 0) {
            alert('Please select an image file');
            return;
        }
        
        const imageFile = imageInput.files[0];
        const targetFormat = targetFormatSelect.value;
        const quality = qualityInput.value;
        
        // Show loading state
        if (resultDiv) {
            resultDiv.innerHTML = 'Converting...';
        }
        
        try {
            // Call the conversion function
            const result = await convertImage(imageFile, targetFormat, quality);
            
            // Show success message
            if (resultDiv) {
                resultDiv.innerHTML = `Conversion successful! Downloaded as ${result.filename}`;
            }
        } catch (error) {
            // Show error message
            if (resultDiv) {
                resultDiv.innerHTML = `Error: ${error.message}`;
            } else {
                alert(`Error: ${error.message}`);
            }
        }
    });
}); 