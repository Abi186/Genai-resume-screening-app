import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/upload"

st.set_page_config(page_title="Resume Screener AI", layout="centered")
st.title("Resume Screener AI")
st.write("Upload a resume and compare it with a job description.")

with st.form("resume_form"):
    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Job Description", height=180)
    submitted = st.form_submit_button("Submit")

if submitted:
    if resume_file is None:
        st.error("Please upload a resume PDF.")
    elif not job_description.strip():
        st.error("Please enter a job description.")
    else:
        files = {
            "file": (resume_file.name, resume_file.getvalue(), "application/pdf"),
        }
        form_data = {"job_description": job_description}

        try:
            with st.spinner("Analyzing resume..."):
                response = requests.post(API_URL, files=files, data=form_data, timeout=120)
        except requests.RequestException as exc:
            st.error(f"Could not connect to backend: {exc}")
        else:
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", "Request failed.")
                except ValueError:
                    detail = "Request failed."
                st.error(detail)
            else:
                try:
                    payload = response.json()
                except ValueError:
                    st.error("Backend returned an invalid response.")
                else:
                    ai_response = payload.get("data", {}).get("ai_response", {})
                    if not ai_response:
                        st.error("No AI response found in backend output.")
                    else:
                        score = ai_response.get("score", 0)
                        skills_matched = ai_response.get("skills_matched", [])
                        missing_skills = ai_response.get("missing_skills", [])
                        decision = ai_response.get("decision", "N/A")

                        st.subheader("Result")
                        st.metric("Score", f"{score}/100")

                        st.write("**Skills Matched**")
                        if skills_matched:
                            for skill in skills_matched:
                                st.write(f"- {skill}")
                        else:
                            st.write("No matched skills found.")

                        st.write("**Missing Skills**")
                        if missing_skills:
                            for skill in missing_skills:
                                st.write(f"- {skill}")
                        else:
                            st.write("No missing skills identified.")

                        st.write("**Decision**")
                        st.info(decision)
