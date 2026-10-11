from fastapi import FastAPI, UploadFile, File
import fitz
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
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""

    for page in doc:
        text = page.get_text()
        if not text.strip():
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
        full_text += "\n" + text

    # --- FIXED EXTRACTION ---

    # 1. Invoice Number - IN26-27/02848097 jaisa
    invoice_no = re.search(r"(?:Invoice\s*No\.?|Bill\s*No\.?)\s*[:\-]?\s*([A-Z0-9\-/]+)", full_text, re.I)
    if not invoice_no:
        invoice_no = re.search(r"\b(IN\d{2}-\d{2}/\d+)\b", full_text)

    # 2. Invoice Date - "Invoice Date: 05-10-2026" ko priority
    date = re.search(r"Invoice\s*Date\s*[:\-]?\s*(\d{2}-\d{2}-\d{4})", full_text, re.I)
    if not date:
        date = re.search(r"Date\s*[:\-]?\s*(\d{2}-\d{2}-\d{4})", full_text, re.I)
    if not date:
        date = re.search(r"\b(\d{2}-\d{2}-\d{4})\b", full_text)

    # 3. Total Amount - IMPORTANT FIX - Longest keyword first
    total = None
    total_patterns = [
        r"Total\s*Invoice\s*Value\s*[:\-]?\s*(\d+\.\d+)",
        r"Grand\s*Total\s*[:\-]?\s*Rs?\.?\s*([\d,]+\.?\d*)",
        r"Total\s*Amount\s*[:\-]?\s*Rs?\.?\s*([\d,]+\.?\d*)",
        r"Invoice\s*Value\s*[:\-]?\s*(\d+\.\d+)",
    ]
    for pat in total_patterns:
        m = re.search(pat, full_text, re.I)
        if m:
            total = m.group(1)
            break
    
    # fallback old logic if not found
    if not total:
        m = re.search(r"Total\s*[:\-]?\s*Rs?\.?\s*([\d,]+\.\d{2})", full_text, re.I)
        if m:
            total = m.group(1)

    return {
        "filename": file.filename,
        "invoice_number": invoice_no.group(1) if invoice_no else "Not Found",
        "date": date.group(1) if date else "Not Found",
        "total_amount": total.replace(',', '') if total else "Not Found",
        "full_text": full_text[:5000],
        "text_preview": full_text[:500]
    }
