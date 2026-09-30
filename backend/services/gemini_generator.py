from __future__ import annotations

from google import genai
from google.genai import types

from backend.config import Settings
from backend.services.fallback_generator import generate_fallback_document


class GeminiDocumentGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None

        if settings.gemini_api_key:
            self.client = genai.Client(api_key=settings.gemini_api_key)

    def _prompt(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        return f"""
Create a professional draft of the following legal document.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{dates}

TERMS / CONDITIONS:
{terms}

Requirements:
- Produce only the document content, not commentary about the prompt.
- Use clear headings and numbered sections.
- Preserve every material user-provided term.
- Do not invent names, dates, addresses, money amounts, obligations, or legal authorities.
- If information is missing, use a clearly marked placeholder such as [INSERT ADDRESS].
- Keep the wording professional and easy to edit.
- Include a signature section where appropriate.
- This is a drafting assistant, not a substitute for advice from a qualified lawyer.
"""

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> tuple[str, bool]:
        if self.settings.demo_mode or not self.client:
            return generate_fallback_document(document_type, parties, terms, dates), True

        try:
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=self._prompt(document_type, parties, terms, dates),
                config=types.GenerateContentConfig(
                    temperature=0.25,
                    max_output_tokens=6000,
                ),
            )
            text = (response.text or "").strip()
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return text, False
        except Exception as exc:
            # Keep the local application usable if the remote model is temporarily
            # unavailable, while making the fallback status visible to the caller.
            fallback = generate_fallback_document(document_type, parties, terms, dates)
            fallback += f"\n\n> AI service fallback: {type(exc).__name__}"
            return fallback, True
