import os
from flask import Flask, request, render_template, redirect, url_for
from PIL import Image
import pytesseract

# Create the Flask app
app = Flask(__name__)

# Configure the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the path to the Tesseract executable (IMPORTANT: Update if your path is different)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/')
def index():
    """Render the upload page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and OCR processing."""
    if 'image' not in request.files:
        return redirect(request.url)
    
    file = request.files['image']
    
    if file.filename == '':
        return redirect(request.url)

    if file:
        # Save the uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            # Use Tesseract to extract text
            with Image.open(filepath) as img:
                extracted_text = pytesseract.image_to_string(img)
        except Exception as e:
            extracted_text = f"An error occurred during OCR: {e}"
        
        # Render the result
        return render_template('result.html', extracted_text=extracted_text)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
