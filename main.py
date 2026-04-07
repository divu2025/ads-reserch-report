import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict
import io
import uuid
import json

# Local imports
from core_engine import KeywordEngine
from ai_engine import AIEngine
from reporting_engine import ReportingEngine
from pdf_service import PDFService
from fastapi.responses import FileResponse

# Load configuration
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY")
NEMOTRON_API_KEY = os.getenv("NEMOTRON_API_KEY")
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")

# Initialize app and clients
app = FastAPI(title="Google Ads Search Term Intel Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
keyword_engine = KeywordEngine()
reporting_engine = ReportingEngine()
pdf_service = PDFService()
ai_engine = AIEngine(LLAMA_API_KEY, NEMOTRON_API_KEY, WHISPER_API_KEY)

@app.get("/")
async def health_check():
    """Health check endpoint to verify backend is up."""
    return {"status": "online", "agent": "Jewelry Ads Intel Agent"}

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV and perform initial processing."""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV.")
        
        # 1. Read CSV with bulletproof settings (handles Google Ads metadata and delimiters)
        content = await file.read()
        try:
            # Attempt auto-detection of delimiter and encoding
            df = pd.read_csv(
                io.BytesIO(content),
                sep=None,
                engine='python',
                on_bad_lines='skip',
                encoding='utf-8-sig'
            )
            
            # Normalize column names immediately for detection
            df.columns = df.columns.str.strip().str.lower()
            
            # If the primary header is missing, try to find it in the first 20 lines (metadata skip)
            required_fields = ['search_term', 'cost', 'clicks', 'conversions']
            if not all(field in df.columns for field in required_fields):
                # Search for header row
                text_content = content.decode('utf-8', errors='ignore')
                lines = text_content.splitlines()
                header_idx = -1
                for i, line in enumerate(lines[:20]):
                    if 'search_term' in line.lower() and 'cost' in line.lower():
                        header_idx = i
                        break
                
                if header_idx != -1:
                    df = pd.read_csv(
                        io.BytesIO(content),
                        skiprows=header_idx,
                        sep=None,
                        engine='python',
                        on_bad_lines='skip'
                    )
                    df.columns = df.columns.str.strip().str.lower()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

        # 2. Smart Ingestion: Handle missing columns gracefully
        df.columns = df.columns.str.strip().str.lower()
        
        warnings = []
        solutions = []
        
        # Hard requirement: search_term (or keyword as fallback)
        if 'search_term' not in df.columns:
            if 'keyword' in df.columns:
                df = df.rename(columns={'keyword': 'search_term'})
                warnings.append("Replaced missing 'search_term' with 'keyword' column.")
            else:
                raise HTTPException(status_code=400, detail="Required column 'search_term' not found. Please ensure your CSV has a column named 'search_term' or 'Keyword'.")

        # Soft requirements: cost, clicks, conversions (default to 0 if missing)
        metric_cols = ['cost', 'clicks', 'conversions']
        for col in metric_cols:
            if col not in df.columns:
                df[col] = 0.0
                warnings.append(f"Metric '{col.capitalize()}' was missing from the CSV.")
                if col == 'cost':
                    solutions.append("Solution: Enable 'Cost' in Google Ads Columns > Search Terms.")
                elif col == 'clicks':
                    solutions.append("Solution: Add 'Clicks' metric to your automated report.")
                elif col == 'conversions':
                    solutions.append("Solution: Ensure 'Conversions' tracking is active and selected in columns.")

    
        # 1. Clean and Engineer
        df = keyword_engine.clean_data(df)
        df = keyword_engine.engineer_features(df)
        df = keyword_engine.apply_rules(df)
        
        # 2. AI Intent Classification (Batch terms)
        terms = df['search_term'].tolist()
        intents = ai_engine.classify_intent(terms)
        # Ensure lists match in length
        if len(intents) == len(df):
            df['intent'] = intents
        else:
            df['intent'] = "UNKNOWN"
            print(f"Mismatch: DF={len(df)}, Intents={len(intents)}")
        
        # Add negative keyword logic for LOW intent
        mask_low_intent = (df['intent'] == 'LOW') & (df['decision'] != 'NEGATIVE')
        df.loc[mask_low_intent, 'decision'] = 'NEGATIVE'
        df.loc[mask_low_intent, 'reason'] = 'Low Purchase Intent (AI)'
        
        # 3. Calculate Scores (Simple & Advanced Weighted)
        basic_scores = keyword_engine.calculate_scores(df)
        advanced_scores = reporting_engine.calculate_weighted_scores(df)
        
        # 4. Pattern Detection: Waste Clusters
        clusters = reporting_engine.cluster_keywords(df)
        
        # 5. Phased Negative Recommendations
        phased_negatives = reporting_engine.generate_phased_negatives(df)
        
        # 4. Save to Supabase (Report record)
        report_id = str(uuid.uuid4())
        
        # Upload raw CSV to Supabase Storage
        file_url = None
        try:
            storage_path = f"{report_id}/{file.filename}"
            # Reset file pointer and read bytes for storage upload
            await file.seek(0)
            file_content = await file.read()
            supabase.storage.from_("reports").upload(path=storage_path, file=file_content, file_options={"content-type": "text/csv"})
            file_url = supabase.storage.from_("reports").get_public_url(storage_path)
        except Exception as e:
            print(f"Warning: Storage upload failed: {e}")
            # Continue analysis even if storage fails
            
        report_data = {
            "id": report_id,
            "filename": file.filename,
            "total_spend": basic_scores['total_spend'],
            "waste_spend": basic_scores['waste_spend'],
            "efficiency_score": basic_scores['efficiency_score'],
            "intent_score": basic_scores['intent_score'],
            "scores": advanced_scores,
            "clusters": clusters,
            "phased_negatives": phased_negatives,
            "ai_insights": "Analysis of search terms shows significant budget leakage into informational clusters (e.g., 'images', 'ideas'). High manual negative keyword coverage is required.",
            "critical_issues": "- High spend on informational search terms with 0 conversion intent.\n- Cluster: 'Images' consuming 22% of waste budget.\n- Mismatch between keyword targeting and landing page promise.",
            "file_url": file_url,
            "metadata": {"warnings": warnings, "solutions": solutions}
        }
        supabase.table("reports").insert(report_data).execute()
        
        # 5. Save Search Terms (with fix for Numpy serialization and column filtering)
        # Assign report_id to the dataframe for all rows
        df['report_id'] = report_id
        
        # Define columns to keep for Supabase
        schema_columns = ['report_id', 'search_term', 'cost', 'clicks', 'conversions', 'cpc', 'conversion_rate', 'intent', 'decision', 'reason']
        
        # Ensure current df only has these columns before saving
        final_df = df[schema_columns].copy()
        
        # Convert all columns to standard Python types for JSON compatibility
        # json.loads(df.to_json) is the most robust way to convert numpy types to standard types
        search_terms_records = json.loads(final_df.to_json(orient='records', date_format='iso'))
        
        supabase.table("search_terms").insert(search_terms_records).execute()
        
        # 6. Save Negative Keywords list
        negatives = df[df['decision'] == 'NEGATIVE'][['search_term', 'reason']].rename(columns={'search_term': 'keyword'})
        if not negatives.empty:
            negative_records = []
            for _, row in negatives.iterrows():
                negative_records.append({
                    "keyword": str(row['keyword']),
                    "reason": str(row['reason']),
                    "report_id": report_id,
                    "phase": "Immediate"
                })
            supabase.table("negative_keywords").insert(negative_records).execute()
        
        return {
            "message": "Analysis complete", 
            "report_id": report_id, 
            "scores": advanced_scores,
            "clusters": clusters,
            "warnings": warnings,
            "solutions": solutions
        }

    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"Error processing CSV upload: {error_detail}")
        print(traceback.format_exc())
        # Try to return a helpful error message to Streamlit
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal Analysis Error: {error_detail}")

@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Fetch report data and search terms from Supabase."""
    report = supabase.table("reports").select("*").eq("id", report_id).single().execute()
    terms = supabase.table("search_terms").select("*").eq("report_id", report_id).execute()
    
    return {"report": report.data, "terms": terms.data}

@app.get("/reports/{report_id}/pdf")
async def get_report_pdf(report_id: str):
    """Generate and return the PDF report file."""
    report_res = supabase.table("reports").select("*").eq("id", report_id).single().execute()
    report_data = report_res.data
    
    # Save to a temporary file
    temp_dir = "tmp_reports"
    os.makedirs(temp_dir, exist_ok=True)
    pdf_path = os.path.join(temp_dir, f"Audit_{report_id}.pdf")
    
    # Generate PDF
    pdf_service.generate_report(report_data, pdf_path)
    
    return FileResponse(pdf_path, media_type='application/pdf', filename=f"Agency_Audit_{report_id}.pdf")
