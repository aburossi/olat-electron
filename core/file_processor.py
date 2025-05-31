import base64
import io
from PIL import Image
import PyPDF2
import docx
from pdf2image import convert_from_bytes
import streamlit as st # For @st.cache_data

@st.cache_data
def convert_pdf_to_images(file_bytes):
    """Convert PDF pages to images."""
    images = convert_from_bytes(file_bytes)
    return images

@st.cache_data
def extract_text_from_pdf(file):
    """Extract text from PDF using PyPDF2."""
    # Ensure the file pointer is at the beginning
    file.seek(0)
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text.strip()

@st.cache_data
def extract_text_from_docx(file):
    """Extract text from DOCX file."""
    # Ensure the file pointer is at the beginning
    file.seek(0)
    doc = docx.Document(file)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text.strip()

def process_image_for_api(_image):
    """
    Process and resize an image to base64 string for API usage.
    Reduces memory footprint.
    """
    if isinstance(_image, (str, bytes)): # If already base64 string or bytes
        if isinstance(_image, str): # If base64 string, decode first
             img_bytes = base64.b64decode(_image)
        else: # If raw bytes
            img_bytes = _image
        img = Image.open(io.BytesIO(img_bytes))
    elif isinstance(_image, Image.Image): # If PIL Image object
        img = _image
    else: # Assume it's a file-like object (e.g., UploadedFile)
        img = Image.open(_image)

    # Convert to RGB mode if it's not
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize if the image is too large
    max_size = 1000  # Reduced max size to reduce memory consumption
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size))

    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG') # Using JPEG for smaller size
    img_byte_arr = img_byte_arr.getvalue()

    return base64.b64encode(img_byte_arr).decode('utf-8')


@st.cache_data
def is_pdf_ocr(text):
    """Placeholder function to determine if PDF is OCRed."""
    # A simple heuristic: if text is very short, it might not be OCRed properly.
    # This is a basic check and can be improved.
    return len(text) > 100 # Arbitrary threshold, adjust as needed

def process_uploaded_pdf(uploaded_file):
    """
    Processes an uploaded PDF file.
    Returns (text_content, images_from_pdf)
    text_content is None if PDF is not OCRed or text extraction fails.
    images_from_pdf is None if text extraction is successful.
    """
    # Ensure the file pointer is at the beginning for multiple reads if necessary
    uploaded_file.seek(0)
    text_content = extract_text_from_pdf(uploaded_file)
    
    uploaded_file.seek(0) # Reset pointer again before potential image conversion
    if text_content and is_pdf_ocr(text_content):
        return text_content, None
    else:
        # Fallback to image processing
        st.warning("Attempting to convert PDF to images as text extraction was insufficient.")
        try:
            images = convert_pdf_to_images(uploaded_file.read())
            return None, images
        except Exception as e:
            st.error(f"Failed to convert PDF to images: {e}")
            return None, None