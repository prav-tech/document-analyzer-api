📄 AI Document Analyzer API

🚀 Overview

This project is an AI-powered document processing system that extracts, analyzes, and summarizes content from multiple document formats including PDF, DOCX, and Images (OCR).

It automatically understands document structure and extracts key information like names, dates, organizations, and more.

✨ Features

- 📂 Multi-format support:
  - PDF
  - DOCX
  - Images (OCR)
- 🔍 Automatic text extraction
- 🧠 AI-based summarization
- 🏷️ Entity extraction:
  - Names
  - Dates
  - Organizations
  - Amounts
  - Locations
- 😊 Sentiment Analysis (Positive / Neutral / Negative)
- 🔐 API Key Authentication

🛠️ Tech Stack

- Python
- FastAPI
- PyMuPDF (PDF processing)
- python-docx (DOCX processing)
- Tesseract OCR (Image text extraction)
- Regex-based NLP

⚙️ Setup Instructions

1. Clone Repository

git clone https://github.com/prav-tech/document-analyzer-api.git
cd document-analyzer-api

2. Install Dependencies

pip install -r requirements.txt

3. Setup Environment Variables

Create a ".env" file and add:

API_KEY=mysecret123

4. Run the Server

uvicorn src.main:app --reload

---
*API Documentation: Swagger UI: https://quickai-qy5b.onrender.com/docs
  -Interactive API documentation available via Swagger UI.

🔌 API Endpoint

POST https://quickai-qy5b.onrender.com/api/document-analyze

Headers:

Content-Type: application/json
X-API-Key: mysecret123

Request Body:

{
  "fileName": "sample1.pdf",
  "fileType": "pdf",
  "fileBase64": "base64 encoded code"
}



✅ Sample Response

{
  "status": "success",
  "fileName": "sample1.pdf",
  "summary": "Technology Industry Analysis: Expansion of Artificial Intelligence Innovation The global technology sector has experienced significant growth in artificial intelligence development over the past few years. Governments, universities, and private companies are increasingly investing in AI research and infrastructure to support innovation across multiple industries. Analysts believe that the continued expansion of artificial intelligence technologies could generate substantial economic and societal benefits in the coming decade. Technology companies such as Google,",
  "entities": {
    "names": [
      "Technology Industry Analysis"
    ]
  },
  "sentiment": "Neutral"
}

🧠 Approach

- Extract text using:
  - PyMuPDF (PDF)
  - python-docx (DOCX)
  - Tesseract OCR (Images)
- Clean and preprocess text
- Apply regex-based entity extraction
- Generate summary using first meaningful sentences
- Perform keyword-based sentiment analysis

🌐 Live API

👉 https://quickai-qy5b.onrender.com/api/document-analyze

📌 Notes

- API requires a valid API key
- Works with base64 encoded files
