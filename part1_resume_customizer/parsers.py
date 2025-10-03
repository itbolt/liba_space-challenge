\
import os
from typing import Optional
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

def read_any(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".txt", ".md"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext in [".pdf"]:
        return pdf_extract_text(path)
    if ext in [".docx"]:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    raise ValueError(f"Unsupported file type: {ext}")

def normalize_text(text: str) -> str:
    # Collapse whitespace and strip
    return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
