# LegalEase — AI-Powered Legal Document Generator

LegalEase is a FastAPI + Streamlit application for generating editable legal-document drafts and exporting them to TXT, DOCX, and PDF.

The project follows the supplied documentation: Streamlit frontend, FastAPI backend, Gemini AI integration, editable preview, and multi-format export.

## Features

- Legal document generation from document type, parties, terms, and effective date
- Gemini integration using the modern `google-genai` SDK
- Built-in demo/template mode so the app can be tested without an API key
- Editable document preview
- TXT, DOCX, and PDF downloads
- Branded DOCX/PDF output with LegalEase logo and footer
- FastAPI `/generate` and `/health` endpoints
- API documentation at `/docs`
- Automated backend tests

## Project structure

```text
LegalEase/
├── assets/
│   └── logo.png
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── document_formatter.py
│       ├── fallback_generator.py
│       └── gemini_generator.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── README.md
└── requirements.txt
```

## 1. VS Code setup

Install Python 3.11 or 3.12.

Open the `LegalEase` folder in VS Code.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Environment configuration

Copy `.env.example` to `.env`.

For the first test, keep:

```env
DEMO_MODE=true
```

This makes LegalEase work without an API key.

For Gemini AI generation, add your key and set:

```env
GEMINI_API_KEY=your_key_here
DEMO_MODE=false
GEMINI_MODEL=gemini-3.8-flash
```

Never commit `.env` to GitHub.

## 3. Start the backend

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## 4. Start the Streamlit frontend

Open a second VS Code terminal:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open the URL Streamlit prints, normally:

```text
http://localhost:8501
```

## 5. Test the complete application

Use:

Document Type:
```text
Freelance Work Contract
```

Parties:
```text
Jane Doe (Service Provider), TechNova Inc. (Client)
```

Terms:
```text
Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice
```

Effective Date:
```text
30 September 2026
```

Click **Generate Document**.

Then edit the generated text and test:

- Download TXT
- Download DOCX
- Download PDF

## 6. Run automated tests

```powershell
pytest -q
```

## AI implementation note

The supplied documentation specifies Gemini 1.5 Pro and the older `google-generativeai` package. This implementation uses the current Google Gen AI Python SDK (`google-genai`) and keeps the model configurable through `GEMINI_MODEL`. The default is `gemini-3.8-flash`; change it in `.env` if your Google AI account exposes a different model.

## Legal safety

LegalEase is an AI-assisted drafting and educational application. Generated content can contain errors or omit jurisdiction-specific requirements. Users should review important documents with a qualified legal professional before signing, filing, or relying on them.
