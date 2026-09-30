from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import html
import re

import requests
import streamlit as st

from backend.services.document_formatter import format_docx, format_pdf, format_txt


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

DEFAULT_BACKEND = "http://127.0.0.1:8000"


def markdown_to_html(text: str) -> str:
    safe = html.escape(text)
    safe = re.sub(r"^# (.+)$", r"<h1>\1</h1>", safe, flags=re.MULTILINE)
    safe = re.sub(r"^## (.+)$", r"<h2>\1</h2>", safe, flags=re.MULTILINE)
    safe = re.sub(r"^\*\*(.+?)\*\*$", r"<strong>\1</strong>", safe, flags=re.MULTILINE)
    safe = re.sub(r"^- (.+)$", r"<li>\1</li>", safe, flags=re.MULTILINE)
    safe = re.sub(r"\n{2,}", "</p><p>", safe)
    safe = safe.replace("\n", "<br>")
    return f"<div class='document-card'><p>{safe}</p></div>"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .main-title { text-align:center; font-size:2.3rem; font-weight:800; margin-bottom:0; }
        .subtitle { text-align:center; color:#9ca3af; margin-bottom:1.5rem; }
        .document-card {
            background:#171923; border:1px solid #343746; border-radius:14px;
            padding:24px; max-height:620px; overflow:auto; line-height:1.7;
        }
        .document-card h1 { text-align:center; color:#e5e7eb; }
        .document-card h2 { color:#93c5fd; margin-top:1.2rem; }
        .document-card li { margin-bottom:0.35rem; }
        .small-note { font-size:0.85rem; color:#9ca3af; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def call_backend(backend_url: str, payload: dict) -> dict:
    response = requests.post(
        f"{backend_url.rstrip('/')}/generate",
        json=payload,
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


inject_css()

st.markdown("<div class='main-title'>⚖️ LegalEase</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>AI-Powered Legal Document Generator</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND)
    st.caption("Start FastAPI before generating a document.")
    st.divider()
    st.markdown("**Supported outputs**")
    st.write("TXT • DOCX • PDF")
    st.markdown(
        "<div class='small-note'>LegalEase creates AI-assisted drafts. Review important documents with a qualified legal professional.</div>",
        unsafe_allow_html=True,
    )

left, right = st.columns([1, 1.4], gap="large")

with left:
    st.subheader("Document Details")
    document_type = st.text_input(
        "Document Type",
        placeholder="e.g. Freelance Work Contract",
    )
    parties = st.text_area(
        "Parties Involved",
        placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
        height=110,
    )
    terms = st.text_area(
        "Terms & Conditions",
        placeholder="Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice",
        height=190,
        help="Separate individual terms with semicolons.",
    )
    dates = st.text_input(
        "Effective Date",
        placeholder="e.g. 30 September 2026",
    )

    generate = st.button("✨ Generate Document", type="primary", use_container_width=True)

with right:
    st.subheader("Document Preview")

    if "generated_text" not in st.session_state:
        st.info("Your generated document will appear here.")

    if generate:
        missing = []
        if not document_type.strip():
            missing.append("Document Type")
        if not parties.strip():
            missing.append("Parties Involved")
        if not terms.strip():
            missing.append("Terms & Conditions")
        if not dates.strip():
            missing.append("Effective Date")

        if missing:
            st.error("Please fill in: " + ", ".join(missing))
        else:
            with st.spinner("Generating your legal document..."):
                try:
                    result = call_backend(
                        backend_url,
                        {
                            "document_type": document_type,
                            "parties": parties,
                            "terms": terms,
                            "dates": dates,
                        },
                    )
                    st.session_state.generated_text = result["document"]
                    st.session_state.doc_type = document_type
                    st.session_state.demo_mode = result.get("demo_mode", False)
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Backend connection failed: {exc}")
                except Exception as exc:
                    st.error(f"Something went wrong: {exc}")

if "generated_text" in st.session_state:
    status = "Demo/template mode" if st.session_state.get("demo_mode") else "Gemini AI mode"
    st.success(f"Document ready • {status}")

    edited = st.text_area(
        "Edit Document Below",
        value=st.session_state.generated_text,
        height=500,
        key="document_editor",
    )
    st.session_state.generated_text = edited

    st.markdown(markdown_to_html(edited), unsafe_allow_html=True)

    txt_data = format_txt(edited)
    docx_data = format_docx(edited, st.session_state.get("doc_type", "Legal Document"))
    pdf_data = format_pdf(edited, st.session_state.get("doc_type", "Legal Document"))

    base_name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        st.session_state.get("doc_type", "legal_document").strip().lower(),
    ).strip("_") or "legal_document"

    st.subheader("Download")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "📄 Download TXT",
            data=txt_data,
            file_name=f"{base_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "📝 Download DOCX",
            data=docx_data,
            file_name=f"{base_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            "📕 Download PDF",
            data=pdf_data,
            file_name=f"{base_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
