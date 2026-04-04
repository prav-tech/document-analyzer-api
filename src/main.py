from dotenv import load_dotenv
load_dotenv()
import re
import base64
import os
import tempfile
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
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

# -------------------------------
# REQUEST MODEL
# -------------------------------
class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

# -------------------------------
# LOAD MODELS (SAFE)
# -------------------------------
# spaCy
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

# Transformers summarizer
try:
    from transformers import pipeline
    summarizer = pipeline("summarization")
except:
    summarizer = None

# -------------------------------
# TEXT EXTRACTION
# -------------------------------
def extract_text(file_path, file_type):
    text = ""
    try:
        if file_type == "pdf":
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()

        elif file_type == "docx":
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                text += "\n"

        elif file_type == "image":
            try:
                img = Image.open(file_path)

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                img = img.convert('L')

                width, height = img.size
                if width < 1000:
                    scale = 1000 / width
                    img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)

                img = ImageEnhance.Contrast(img).enhance(2.0)
                img = img.filter(ImageFilter.SHARPEN)

                img_np = np.array(img)
                img_np = (img_np > 150) * 255
                img = Image.fromarray(img_np.astype('uint8'))

                text = pytesseract.image_to_string(img, config='--oem 3 --psm 6').strip()

                if not text:
                    text = pytesseract.image_to_string(img, config='--oem 3 --psm 3').strip()

                if not text:
                    text = "No text found in image"

            except Exception as e:
                text = f"Error processing image: {str(e)}"

    except Exception as e:
        text = f"Error extracting text: {str(e)}"

    return text

# -------------------------------
# SENTIMENT
# -------------------------------
def get_sentiment(text):
    positive = {"good","excellent","profit","success","approved","paid","great","happy"}
    negative = {"loss","failed","rejected","error","issue","problem","delay"}

    words = set(text.lower().split())
    pos = len(words & positive)
    neg = len(words & negative)

    if pos > neg:
        return "Positive"
    elif neg > pos:
        return "Negative"
    return "Neutral"

# -------------------------------
# ENTITY EXTRACTION
# -------------------------------
def extract_entities(text):
    entities = {
        "names": [],
        "dates": [],
        "organizations": [],
        "amounts": [],
        "locations": []
    }

    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                entities["names"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
            elif ent.label_ == "ORG" and ent.text.lower() != "html":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "MONEY":
                entities["amounts"].append(ent.text)
            elif ent.label_ == "GPE":
                entities["locations"].append(ent.text)

    return {k: list(set(v)) for k, v in entities.items()}

# -------------------------------
# SUMMARY
# -------------------------------
def summarize_text(text):
    if not text:
        return ""

    text = text[:1000]

    if summarizer:
        try:
            result = summarizer(text, max_length=60, min_length=20, do_sample=False)
            return result[0]['summary_text']
        except:
            pass

    sentences = text.split(".")
    return sentences[0] if sentences else text[:100]

# -------------------------------
# MAIN ANALYSIS
# -------------------------------
def analyze_document(file_name, text):
    entities = extract_entities(text)
    sentiment = get_sentiment(text)
    summary = summarize_text(text)

    return {
        "status": "success",
        "fileName": file_name,
        "summary": summary,
        "entities": entities,
        "sentiment": sentiment
    }

# -------------------------------
# API ROUTES
# -------------------------------
@app.get("/")
def home():
    return {"message": "API is working 🚀"}

@app.post("/api/document-analyze")
def analyze_api(request: DocumentRequest, x_api_key: str = Header(None)):

    API_KEY = os.getenv("API_KEY")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        file_data = base64.b64decode(request.fileBase64)

        suffix_map = {"pdf": ".pdf", "docx": ".docx", "image": ".png"}
        suffix = suffix_map.get(request.fileType, ".tmp")

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_data)
            file_path = tmp.name

        try:
            text = extract_text(file_path, request.fileType)
            result = analyze_document(request.fileName, text)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

        return result

    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e)}