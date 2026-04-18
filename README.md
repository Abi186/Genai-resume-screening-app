# AI Resume Screener

AI-powered Resume Screener built using FastAPI and Streamlit. The application extracts text from PDF resumes, compares it with job descriptions using OpenAI, and generates a match score, skill analysis, and hiring recommendation.

 **Features**
- Upload PDF resumes
- Enter job description
- Extract text from resumes
- AI-based skill matching
- Score calculation
- Hiring recommendation

---
**Tech Stack**
- Python
- FastAPI (Backend)
- Streamlit (Frontend)
- OpenAI API (AI processing)
- pdfplumber (PDF extraction)
---

##  How It Works
1. User uploads resume and enters job description  
2. Backend extracts text from PDF  
3. AI compares resume with job description  
4. Returns:
   - Match Score  
   - Skills Matched  
   - Missing Skills  
   - Hiring Decision  

## ▶️ Run Locally

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn main:app --reload

# Run frontend
streamlit run app.py

**Future Improvements**
- Multiple resume comparison
- Candidate ranking system
- Database integration
- Deployment (Render + Streamlit Cloud)

**Author**
Abi Nantha
