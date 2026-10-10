pythonfrom fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import PyPDF2, io, re

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h2>P2P Agent Live!</h2><a href='/docs'>API Docs pe jao</a>"

@app.post("/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    data = await file.read()
    reader = PyPDF2.PdfReader(io.BytesIO(data))
    text = "".join([p.extract_text() or "" for p in reader.pages])
    return {"filename": file.filename, "text_preview": text[:1000]}
