
from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF
import re
import io
from PIL import Image
import pytesseract

app = FastAPI(title="P2P Invoice Agent")

@app.get("/")
def home():
    return {"message": "P2P Agent Live! Go to /docs"}

@app.post("/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    # Read PDF
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    
    for page in doc:
        text = page.get_text()
        if not text.strip():
            # If no text, try OCR
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
        full_text += text + "\n"

    # Simple extraction
    invoice_no = re.search(r'(Invoice\s*No\.?|Bill\s*No\.?)\s*[:\-]?\s*(\S+)', full_text, re.I)
    date = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', full_text)
    total = re.search(r'(Grand\s*Total|Total\s*Amount|Total)\s*[:\-]?\s*₹?\s*([\d,]+\.?\d*)', full_text, re.I)

    return {
        "filename": file.filename,
        "invoice_number": invoice_no.group(2) if invoice_no else "Not Found",
        "date": date.group(1) if date else "Not Found",
        "total_amount": total.group(2) if total else "Not Found",
        "full_text": full_text[:2000],  # first 2000 chars
        "text_preview": full_text[:500]
    }
