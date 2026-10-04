from fastapi import APIRouter, HTTPException

from backend.config import get_settings
from backend.schemas import DocumentRequest, DocumentResponse
from backend.services.gemini_generator import GeminiDocumentGenerator


router = APIRouter()
settings = get_settings()
generator = GeminiDocumentGenerator(settings)


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "ai_configured": bool(settings.gemini_api_key),
        "demo_mode": settings.demo_mode,
        "model": settings.gemini_model,
    }


@router.post("/generate", response_model=DocumentResponse)
def generate_legal_document(request: DocumentRequest) -> DocumentResponse:
    try:
        document, demo_mode = generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
        return DocumentResponse(
            document=document,
            model=settings.gemini_model,
            demo_mode=demo_mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {exc}") from exc
