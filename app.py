import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from src.extractor import extract_location

load_dotenv()

st.set_page_config(
    page_title="AI Location Extractor",
    page_icon="📍",
    layout="wide",
)

st.title("📍 AI Location Extraction Demo")
st.markdown("""
Extract structured location data from job posting text using GPT-4o-mini.

This demo showcases how LLMs can replace manual data extraction tasks at ~$0.0002 per extraction.
""")

# Sidebar for API key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key. Get one at platform.openai.com"
    )
    
    st.markdown("---")
    st.markdown("""
    ### How it works
    1. Paste job posting text
    2. Click "Extract Location"
    3. View structured results
    
    ### Cost
    ~$0.0002 per extraction using GPT-4o-mini
    """)

# Sample job posting for demo
SAMPLE_JOB = """Software Engineer - Backend

Location: Austin, TX 78701 (Hybrid)

About the Role:
We're looking for a talented backend engineer to join our growing team. You'll work on our core platform services, building scalable APIs and data pipelines.

Requirements:
- 3+ years of experience with Python or Go
- Experience with distributed systems
- Strong communication skills

Benefits:
- Competitive salary
- Health, dental, and vision insurance
- Flexible PTO
- Remote work options available

Apply at careers@example.com

Example Corp
123 Main Street, Suite 400
Austin, TX 78701
"""

# Main input area
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    
    if st.button("Load Sample"):
        st.session_state.job_text = SAMPLE_JOB
    
    job_text = st.text_area(
        "Job Posting Text",
        value=st.session_state.get("job_text", ""),
        height=400,
        placeholder="Paste job posting text here..."
    )

with col2:
    st.subheader("Extraction Results")
    
    if st.button("Extract Location", type="primary", disabled=not api_key):
        if not job_text.strip():
            st.warning("Please enter some job posting text.")
        else:
            with st.spinner("Extracting location..."):
                try:
                    client = OpenAI(api_key=api_key)
                    result = extract_location(job_text, client)
                    
                    st.success("Extraction complete!")
                    
                    st.metric("Location", result.answer)
                    st.metric("Granularity", result.granularity)
                    
                    if result.is_remote:
                        st.info(f"🏠 Remote/Hybrid indicators found: {', '.join(result.remote_indicators)}")
                    
                    with st.expander("Explanation"):
                        st.write(result.explanation)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Built by <a href="https://geoalchemist.com">Wes Porter</a> | 
    <a href="https://github.com/wessport/ai-loc-extraction-demo">GitHub</a>
</div>
""", unsafe_allow_html=True)
