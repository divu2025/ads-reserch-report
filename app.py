import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Jewelry Ads Intel Agent", layout="wide", page_icon="💍")

# Styling
st.markdown("""
<style>
    .main {
        background-color: #0f1116;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1a1e26;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("💍 AI Search Term Intelligence Agent")
st.subheader("Personal Decision Engine for Jewelry Google Ads")

# --- Sidebar: Upload & History ---
with st.sidebar:
    st.header("📤 Ingestion")
    uploaded_file = st.file_uploader("Upload Search Term CSV", type=["csv"])
    
    if uploaded_file and st.button("🚀 Run Analysis"):
        with st.spinner("Analyzing with NVIDIA AI..."):
            files = {"file": uploaded_file.getvalue()}
            # Note: streamlit needs the filename
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            
            try:
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success("Analysis Complete!")
                    st.session_state['report_id'] = response.json()['report_id']
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")

# --- Dashboard: Report View ---
if 'report_id' in st.session_state:
    report_id = st.session_state['report_id']
    
    # Fetch report from backend
    try:
        report_data = requests.get(f"{API_URL}/reports/{report_id}").json()
        report = report_data['report']
        terms_df = pd.DataFrame(report_data['terms'])
        
        # Header & Downloads
        st.header(f"📊 Agency Audit: {report['filename']}")
        
        d_col1, d_col2, d_col3 = st.columns([2, 1, 1])
        with d_col2:
            st.link_button("📄 Download PDF Audit", f"{API_URL}/reports/{report_id}/pdf")
        with d_col3:
            csv_raw = terms_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Analysis CSV", csv_raw, "analysis_results.csv", "text/csv")
            
        # 🟢 Tabbed Professional Report
        tab_summary, tab_analysis, tab_strategy, tab_status = st.tabs(["📋 Executive Summary", "🔍 In-Depth Analysis", "🗺️ Strategy Roadmap", "⚙️ System Status"])
        
        with tab_summary:
            # 1. Executive Summary
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Spend", f"${report['total_spend']:,.2f}")
            col2.metric("Waste Spend", f"${report['waste_spend']:,.2f}", f"-{report['total_spend'] - report['waste_spend']:.0f}%", delta_color="inverse")
            col3.metric("Overall Score", f"{report.get('scores', {}).get('overall_score', 0)}/100")
            col4.metric("High Intent", f"{report['intent_score']:.1f}%")
            
            st.divider()
            
            # 2. Score Breakdown
            st.subheader("📊 2. Score Breakdown")
            s_col1, s_col2, s_col3 = st.columns(3)
            adv_scores = report.get('scores', {})
            s_col1.progress(adv_scores.get('intent_quality', 0) / 100, text=f"Search Intent Quality: {adv_scores.get('intent_quality', 0)}")
            s_col2.progress(adv_scores.get('waste_control', 0) / 100, text=f"Waste Spend Control: {adv_scores.get('waste_control', 0)}")
            s_col3.progress(adv_scores.get('conversion_efficiency', 0) / 100, text=f"Conversion Performance: {adv_scores.get('conversion_efficiency', 0)}")
            
            # 3. Critical Issues
            st.subheader("🚨 3. Top Critical Issues")
            st.error(report.get('critical_issues', "No critical issues detected."))
            
            # 10. AI Insights
            st.subheader("🧠 10. AI Agency Insights")
            st.info(report.get('ai_insights', "Analysis complete. Budget allocation should focus on high-intent conversion clusters."))

        with tab_analysis:
            # 4. Search Term Analysis
            st.subheader("🔍 4. Search Term Analysis (Core)")
            st.dataframe(terms_df[['search_term', 'cost', 'clicks', 'conversions', 'intent', 'decision', 'reason']], use_container_width=True)
            
            # 5. Intent Analysis
            st.subheader("🧠 5. Intent Analysis Breakdown")
            intent_counts = terms_df['intent'].value_counts(normalize=True) * 100
            i_col1, i_col2, i_col3 = st.columns(3)
            i_col1.metric("High", f"{intent_counts.get('HIGH', 0):.1f}%")
            i_col2.metric("Medium", f"{intent_counts.get('MEDIUM', 0):.1f}%")
            i_col3.metric("Low", f"{intent_counts.get('LOW', 0):.1f}%")
            
            # 6. Waste Spend Analysis
            st.subheader("💸 6. Waste Spend Analysis")
            clusters = report.get('clusters', [])
            if clusters:
                cluster_df = pd.DataFrame(clusters)
                st.bar_chart(cluster_df, x='label', y='cost', color='#ff4444')
            
            # 7. Keyword Cluster Analysis
            st.subheader("🧩 7. Keyword Waste Clusters")
            for c in clusters:
                st.write(f"**{c['label']}** (${c['cost']:,.2f})")
                st.caption(f"Patterns: {c['terms']}")

        with tab_strategy:
            # 8. Negative Keyword Recommendations
            st.subheader("🚫 8. Negative Keyword Recommendations (Phased)")
            phased = report.get('phased_negatives', {})
            p_col1, p_col2, p_col3 = st.columns(3)
            p_col1.write("### Phase 1: Immediate")
            p_col1.write(", ".join(phased.get('Phase 1 (Immediate)', [])[:10]))
            p_col2.write("### Phase 2: Intent")
            p_col2.write(", ".join(phased.get('Phase 2 (Intent Based)', [])[:10]))
            p_col3.write("### Phase 3: Data")
            p_col3.write(", ".join(phased.get('Phase 3 (Data Based)', [])[:10]))
            
            # 11. Action Plan
            st.divider()
            st.subheader("⚙️ 11. Action Plan (Prioritized)")
            st.success("🟢 Scale: Focus on keywords with >5% Conversion Rate and High Intent.")
            st.warning("🟠 Optimization: Restructure clusters into single-keyword ad groups.")
            st.error("🔴 Critical: Pause all keywords in the 'Waste' clusters immediately.")
            
            # 12. 4-Week Roadmap
            st.subheader("🗺️ 12. 4-Week Growth Roadmap")
            roadmap_data = {
                "Week": ["Week 1", "Week 2", "Week 3", "Week 4"],
                "Focus": ["Negative Cleanup", "Structure Fix", "Scale High Intent", "Perf Audit"]
            }
            st.table(pd.DataFrame(roadmap_data))
            
            # 13. Methodology
            st.caption("---")
            st.caption("🧠 13. Methodology: Processed using Python NLP + Llama 3.1 & TF-IDF Clustering.")

        with tab_status:
            st.subheader("⚙️ Analysis Process & System Status")
            
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.write("### 🧠 The Analysis Process")
                st.write("1. **Smart Ingestion**: Bypasses header metadata.")
                st.write("2. **Data Normalization**: Cleans currency & metrics.")
                st.write("3. **AI Classification**: Intent grouping (Llama 3.1).")
                st.write("4. **Semantic Clustering**: Waste pattern detection.")
                st.write("5. **Agency Scoring**: Weighted 0-100 metrics.")
                st.write("6. **Narrative Generation**: AI-driven insights.")
            
            with col_s2:
                st.write("### ⏱️ Estimated Timing")
                st.metric("Avg. Processing Time", "10-15s")
                st.write("- **Ingestion**: <1s")
                st.write("- **AI Batching**: 5-8s")
                st.write("- **Clustering**: 1-2s")
                st.write("- **PDF Render**: 2s")

            st.divider()
            
            st.write("### ✅ Done Steps (System Readiness)")
            done_data = {
                "Component": ["Backend Resilience", "AI Intent Engine", "Clustering Engine", "Agency Dashboard", "PDF Export"],
                "Status": ["✅ Done", "✅ Done", "✅ Done", "✅ Done", "✅ Done"]
            }
            st.table(pd.DataFrame(done_data))

    except Exception as e:
        import traceback
        st.error(f"Error loading report: {e}")
        st.code(traceback.format_exc())
else:
    st.info("Upload a CSV file to get started.")
    st.markdown("""
    ### Help: How to download the right report?
    1. Go to **Google Ads Dashboard**.
    2. Select **Keywords** > **Search Terms**.
    3. Choose a time range (e.g., Last 30 Days).
    4. Click **Download** > **CSV**.
    5. Ensure columns include: `search_term`, `cost`, `clicks`, `conversions`.
    """)
