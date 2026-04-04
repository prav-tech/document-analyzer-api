# 📄 Data Extraction API

---
## 🧠 Description

This project is an AI-powered Document Analyzer API built using FastAPI. It processes documents (PDF, DOCX, and images) by extracting text, generating summaries, identifying key entities, and performing sentiment analysis.

The system accepts files in Base64 format, decodes them, extracts content using OCR or parsing techniques, and applies NLP-based analysis to return structured insights.

---
## ⚙️ Tech Stack

* **Language/Framework:** Python, FastAPI
* **Key Libraries:** Uvicorn, Pydantic, Base64, pytesseract, PIL
* **AI/NLP:** Basic NLP techniques for summarization and sentiment analysis

---
## 🛠️ Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/prav-tech/document-analyzer-api.git
cd document-analyzer-api
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set environment variables**
   Create a `.env` file:

```
API_KEY=your_secret_key
```

4. **Run the application**

```bash
uvicorn src.main:app --reload
```

5. Open in browser:

```
http://127.0.0.1:8000/docs
```

---

## 🔍 Approach

1. **Input Handling**

   * Accept document as Base64 string
   * Identify file type (PDF, DOCX, Image)

2. **File Processing**

   * Decode Base64 to file
   * Save temporarily

3. **Text Extraction**

   * PDFs/DOCX → direct parsing
   * Images → OCR using Tesseract

4. **Analysis**

   * Generate summary
   * Extract entities (names, dates, organizations, etc.)
   * Perform sentiment analysis

5. **Output**

   * Return structured JSON response

---

## 🚀 Live API

* [https://quickai-qy5b.onrender.com](https://quickai-qy5b.onrender.com)
* Swagger Docs: [https://quickai-qy5b.onrender.com/docs](https://quickai-qy5b.onrender.com/docs)

---

## 📦 API Endpoint

### POST `/api/document-analyze`

**Headers:**

```
x-api-key: your_secret_key
Content-Type: application/json
```

**Request Body:**

```json
{
  "fileName": "sample.pdf",
  "fileType": "pdf",
  "fileBase64": "BASE64_STRING"
}
```
## 📤 Sample Response

```json
{
  "status": "success",
  "fileName": "sample.pdf",
  "summary": "Short summary...",
  "entities": {
    "names": [],
    "dates": [],
    "organizations": [],
    "amounts": [],
    "locations": []
  },
  "sentiment": "Neutral"
}
```
## 📌 Status

✅ API working
✅ Deployed on Render
✅ Tested using Postman & Swagger

## 👩‍💻 Author
Pravallika B
