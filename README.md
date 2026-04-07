# 💠 Jewelry Ads Intel Agent

An AI-powered personal decision engine for auditing Google Ads search term reports.

## Features
- **CSV Ingestion**: Upload standard Google Ads search term reports.
- **Rule-Based Filtering**: Identify obvious waste based on cost and conversions.
- **NVIDIA AI Intent Classification**: Analyze keyword intent (HIGH/MEDIUM/LOW) using Llama 3.1 70B.
- **Jewelry Market Logic**: Custom personas for accurate audit of jewelry-specific terms.
- **Supabase Integration**: Persistent storage for all audits and negative keyword lists.
- **Streamlit Dashboard**: Professional UI with Plotly visualizations and export capabilities.

## Tech Stack
- **Backend**: FastAPI
- **AI**: NVIDIA NIM (Llama 3.1, Nemotron-4, Arctic Embed)
- **Database**: Supabase
- **Frontend**: Streamlit

## Setup
1.  Run `database_schema.sql` in Supabase SQL editor.
2.  Configure `.env` with your Supabase and NVIDIA credentials.
3.  Install: `pip install -r requirements.txt`.
4.  Run Backend: `uvicorn main:app --reload`.
5.  Run UI: `streamlit run app.py`.

*Developed by Antigravity AI Agent.*
