from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from utils.helpers import (
    PdfExtractionError,
    analyze_resume,
    extract_text_from_pdf,
    normalize_text,
)

app = FastAPI(title="Resume Screener AI")


@app.get("/")
def home():
    return {"message": "Resume Screener AI backend is running."}


@app.get("/health")
def health_check():
    sample = normalize_text("  Resume Screener Ready  ")
    return {"status": "ok", "sample_text": sample}


@app.post("/upload")
async def upload_resume(
    file: UploadFile | None = File(None),
    job_description: str | None = Form(None),
):
    if file is None:
        raise HTTPException(status_code=400, detail="Resume file is required.")

    filename = normalize_text(file.filename or "")
    if not filename:
        raise HTTPException(status_code=400, detail="Resume filename is missing.")

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    cleaned_job_description = normalize_text(job_description or "")
    if not cleaned_job_description:
        raise HTTPException(status_code=400, detail="Job description is required.")

    try:
        file_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to read uploaded file.")
    finally:
        await file.close()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty. Please upload a valid PDF.")

    try:
        extracted_text = extract_text_from_pdf(file_bytes)
    except PdfExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        analysis = analyze_resume(extracted_text, cleaned_job_description)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to analyze resume.")

    return {
        "status": "success",
        "data": {
            "file": {"name": filename},
            "resume": {
                "preview": extracted_text[:500],
                "characters": len(extracted_text),
            },
            "ai_response": {
                "score": analysis["score"],
                "skills_matched": analysis["skills_matched"],
                "missing_skills": analysis["missing_skills"],
                "summary": analysis["summary"],
                "decision": analysis["decision"],
            },
        },
    }
