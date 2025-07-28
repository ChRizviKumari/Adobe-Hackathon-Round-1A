import fitz  # PyMuPDF
from utils.outline_extractor import extract_outline_and_title

def parse_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    result = extract_outline_and_title(doc)
    doc.close()
    return result
