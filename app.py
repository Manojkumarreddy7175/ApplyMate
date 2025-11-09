import streamlit as st
import pandas as pd
import asyncio
import os
import json
from agent import run_job_agent, parse_resume, collect_preferences

st.title("MCP Job Application Agent Dashboard")

uploaded_resume = st.file_uploader("Upload Your Resume (PDF)", type="pdf")
resume_path = "temp_resume.pdf"
if uploaded_resume:
    with open(resume_path, "wb") as f:
        f.write(uploaded_resume.getvalue())
    st.success(f"Resume uploaded and saved to {resume_path}!")

    # Parse resume asynchronously
    with st.spinner("Parsing resume for preferences..."):
        resume_data = asyncio.run(parse_resume(resume_path))
    
    # Display extracted data and prompt for confirmation/adjustments
    st.subheader("Resume Extracted Preferences")
    st.json(resume_data)
    
    # Collect additional preferences
    job_title = st.text_input("Preferred Job Title", resume_data.get("preferred role", "Software Engineer"))
    location = st.text_input("Location", resume_data.get("location", "Remote"))
    min_salary = st.number_input("Minimum Salary", value=resume_data.get("minimum salary expectation", 100000))
    skills = st.text_area("Skills (comma-separated)", ",".join(resume_data.get("skills", ["Python", "AI"]))).split(",")

    if st.button("Run Agent Now"):
        prefs = {
            "title": job_title,
            "location": location,
            "min_salary": min_salary,
            "skills": [s.strip() for s in skills]
        }
        with open('preferences.json', 'w') as f:
            json.dump(prefs, f)
        
        with st.spinner("Running MCP Agent: Scraping, Filtering, Applying..."):
            result = asyncio.run(run_job_agent(resume_path=resume_path))
            st.write("Agent Result:")
            st.text(result)

try:
    df = pd.read_csv('jobs_dashboard.csv')
    st.subheader("Filtered Jobs Dashboard")
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), "filtered_jobs.csv")
    title_filter = st.text_input("Filter by Title")
    filtered = df[df['title'].str.contains(title_filter, case=False, na=False)] if title_filter else df
    st.dataframe(filtered)
except FileNotFoundError:
    st.info("Run the agent to generate job data.")