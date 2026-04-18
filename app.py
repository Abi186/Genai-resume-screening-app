import streamlit as st
import requests

st.title("Resume Screener AI")

file = st.file_uploader("Upload Resume (PDF)")
job_description = st.text_area("Paste Job Description")

if st.button("Analyze Resume"):
    if file and job_description:
        with st.spinner("Analyzing..."):
            response = requests.post(
                "http://127.0.0.1:8000/upload",
                files={"file": file},
                data={"job_description": job_description}
            )

            if response.status_code == 200:
                data = response.json()["data"]["ai_response"]

                st.success("Analysis Complete")

                st.write("Score:", data["score"])
                st.write("Matched Skills:", data["skills_matched"])
                st.write("Missing Skills:", data["missing_skills"])
                st.write("Summary:", data["summary"])
                st.write("Decision:", data["decision"])
            else:
                st.error("Something went wrong")
    else:
        st.warning("Upload file and enter job description")