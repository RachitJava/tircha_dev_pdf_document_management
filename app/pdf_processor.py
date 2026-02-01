import fitz  # PyMuPDF
import base64
from io import BytesIO

def process_pdf(file_input):
    """
    Returns a tuple (searchable_text, pdf_base64)
    """
    try:
        if hasattr(file_input, 'read'):
            pdf_bytes = file_input.read()
        else:
            pdf_bytes = file_input
            
        # 1. Extract text for search index
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_content = ""
        for page in doc:
            text_content += page.get_text()
        doc.close()
        
        # 2. Encode to Base64 for storage in JSON
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        
        return text_content, pdf_base64

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return str(e), ""
