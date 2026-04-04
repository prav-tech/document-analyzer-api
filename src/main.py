from dotenv import load_dotenv
load_dotenv()

import re
import base64
import os
import io

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import fitz
from docx import Document
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import numpy as np

# -------------------------------
# CONFIG
# -------------------------------
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# REQUEST MODEL
# -------------------------------
class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

# -------------------------------
# OPTIONAL MODELS
# -------------------------------
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

try:
    from transformers import pipeline
    summarizer = pipeline("summarization")
except:
    summarizer = None

# -------------------------------
# ROUTES
# -------------------------------
@app.get("/")
def home():
    return {"message": "API is working 🚀"}
@app.post("/")
def root_post():
    return {
        "status": "success",
        "fileName": "test",
        "summary": "API working",
        "entities": [],
        "sentiment": "neutral"
    }
@app.post("/api/document-analyze")
def analyze_api(request: DocumentRequest, x_api_key: str = Header(None)):

    if x_api_key != "mysecret123":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        file_data = base64.b64decode(request.fileBase64)
        file_type = request.fileType.lower()

        extracted_text = ""

        # -------------------------------
        # PDF
        # -------------------------------
        if file_type == "pdf":
            try:
                doc = fitz.open(stream=file_data, filetype="pdf")
                for page in doc:
                    extracted_text += page.get_text()
            except:
                extracted_text = "Could not read PDF"

        # -------------------------------
        # DOCX
        # -------------------------------
        elif file_type == "docx":
            try:
                doc = Document(io.BytesIO(file_data))
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"
            except:
                extracted_text = "Could not read DOCX"

        # -------------------------------
        # IMAGE (OCR)
        # -------------------------------
        elif file_type in ["png", "jpg", "jpeg"]:
            try:
                img = Image.open(io.BytesIO(file_data)).convert("L")
                img = ImageEnhance.Contrast(img).enhance(2.0)
                img = img.filter(ImageFilter.SHARPEN)

                img_np = np.array(img)
                img_np = (img_np > 150) * 255
                img = Image.fromarray(img_np.astype('uint8'))

                extracted_text = pytesseract.image_to_string(img).strip()
            except:
                extracted_text = "Could not read image"

        # -------------------------------
        # TEXT FALLBACK
        # -------------------------------
        else:
            try:
                extracted_text = file_data.decode("utf-8", errors="ignore")
            except:
                extracted_text = "Unsupported file type"

        # -------------------------------
        # SAFETY
        # -------------------------------
        if not extracted_text.strip():
            extracted_text = "No readable content found"

        # -------------------------------
        # SUMMARY
        # -------------------------------
        if summarizer:
            try:
                result = summarizer(extracted_text[:1000], max_length=100, min_length=70)
                summary = result[0]["summary_text"]
            except:
                summary = " ".join(extracted_text.split()[:80])
        else:
            summary = " ".join(extracted_text.split()[:80])

        # -------------------------------
        # ENTITIES (basic fallback)
        # -------------------------------
        entities = []
        for word in extracted_text.split():
            if word.istitle():
                entities.append(word)

        # -------------------------------
        # SENTIMENT
        # -------------------------------
        sentiment = "neutral"
        text_lower = extracted_text.lower()

        if any(w in text_lower for w in ["good", "great", "growth", "success", "innovation"]):
            sentiment = "positive"
        elif any(w in text_lower for w in ["bad", "loss", "decline"]):
            sentiment = "negative"

        # -------------------------------
        # EXTRA FIELDS
        # -------------------------------
        names = list(set([w for w in extracted_text.split() if w.istitle()]))[:10]
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', extracted_text)

        org_keywords = ["Inc", "Ltd", "Corporation", "Company", "University", "Institute"]
        organizations = []
        for word in extracted_text.split():
            for key in org_keywords:
                if key in word:
                    organizations.append(word)

        amounts = re.findall(r'[\$₹]\d+(?:,\d+)*(?:\.\d+)?', extracted_text)

        # -------------------------------
        # FINAL RESPONSE
        # -------------------------------
        return {
            "status": "success",
            "file_name": request.fileName,
            "summary": summary,
            "entities": list(set(entities))[:10],
            "sentiment": sentiment,
            "names": names,
            "dates": dates,
            "organizations": list(set(organizations)),
            "amounts": amounts
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
