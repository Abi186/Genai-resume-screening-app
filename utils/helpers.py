import io
import json
import os
import re

import pdfplumber
from openai import OpenAI
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.psparser import PSEOF

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Replace with your key or use env var OPENAI_API_KEY


class PdfExtractionError(Exception):
    """
    Raised when PDF extraction fails due to invalid or unreadable files.
    """


def normalize_text(text: str) -> str:
    """
    Basic text cleaner used as a placeholder utility.
    """
    return " ".join(text.strip().split())


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from all pages in a PDF.
    """
    if not file_content:
        raise PdfExtractionError("Uploaded file is empty. Please upload a valid PDF.")

    pages_text = []
    pdf_stream = io.BytesIO(file_content)
    try:
        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    pages_text.append(page_text)
    except (PDFSyntaxError, PSEOF):
        raise PdfExtractionError("Invalid PDF file. Please upload a valid PDF.")
    except Exception:
        raise PdfExtractionError("Unable to read this PDF file. Please try another PDF.")

    full_text = "\n".join(pages_text).strip()
    if not full_text:
        return ""

    return normalize_text(full_text)


def _parse_json_object(raw_content: str) -> dict:
    """
    Parse a JSON object from model output with a simple fallback.
    """
    if not raw_content:
        return {}

    try:
        data = json.loads(raw_content)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_content)
    if not match:
        return {}

    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def _clean_string_list(value) -> list[str]:
    """
    Ensure a clean list of non-empty strings.
    """
    if isinstance(value, str):
        value = value.split(",")

    if not isinstance(value, list):
        return []

    cleaned = []
    for item in value:
        text = normalize_text(str(item))
        if text:
            cleaned.append(text)
    return cleaned


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Compare resume text with a job description using OpenAI Chat Completions.
    """
    resume_text = normalize_text(resume_text or "")
    job_description = normalize_text(job_description or "")

    if not resume_text:
        return {
            "score": 0,
            "skills_matched": [],
            "missing_skills": [],
            "summary": "No readable text was found in the uploaded resume.",
            "decision": "Reject",
        }

    api_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
    if api_key == "YOUR_OPENAI_API_KEY":
        raise ValueError("Please set your OpenAI API key before calling analyze_resume.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
Compare the resume and job description.
Return valid JSON only with these keys:
- score (0-100 integer)
- skills_matched (array of strings)
- missing_skills (array of strings)
- summary (short paragraph)
- decision (Hire or Reject)

Resume:
{resume_text}

Job Description:
{job_description}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert recruiter. Be fair, concise, and consistent.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    data = _parse_json_object(content)

    score_raw = data.get("score", 0)
    try:
        score = int(float(score_raw))
    except (TypeError, ValueError):
        score = 0
    score = max(0, min(100, score))

    decision = normalize_text(str(data.get("decision", "Reject")))
    if not decision:
        decision = "Reject"

    skills_matched_raw = data.get("skills_matched", data.get("matching_skills", []))
    skills_matched = _clean_string_list(skills_matched_raw)
    missing_skills = _clean_string_list(data.get("missing_skills", []))
    summary = normalize_text(str(data.get("summary", "")))

    return {
        "score": score,
        "skills_matched": skills_matched,
        "missing_skills": missing_skills,
        "summary": summary,
        "decision": decision,
    }
