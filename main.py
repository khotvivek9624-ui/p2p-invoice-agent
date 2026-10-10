
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import PyPDF2, io

app = FastAPI()

@app.get("/")
def home():
    return {"message": "P2P Agent Live! Go to /docs"}

@app.post("/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    data = await file.read()
    reader = PyPDF2.PdfReader(io.BytesIO(data))
    text = ""
    for p in reader.pages:
        text += p.extract_text() or ""
    return {"filename": file.filename, "text_preview": text[:1000]}
