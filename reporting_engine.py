import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List, Dict

class ReportingEngine:
    def __init__(self):
        pass

    def calculate_weighted_scores(self, df: pd.DataFrame) -> Dict:
        """Calculate professional agency-grade scores (0-100)."""
        # 1. Search Intent Quality
        high_intent_ratio = (len(df[df['intent'] == 'HIGH']) / len(df)) if len(df) > 0 else 0
        intent_score = min(100, int(high_intent_ratio * 150)) # Weighted
        
        # 2. Waste Spend Control
        total_spend = df['cost'].sum()
        waste_spend = df[df['decision'] == 'NEGATIVE']['cost'].sum()
        waste_ratio = (waste_spend / total_spend) if total_spend > 0 else 0
        waste_control_score = max(0, 100 - int(waste_ratio * 200))
        
        # 3. Conversion Performance
        total_conv = df['conversions'].sum()
        total_clicks = df['clicks'].sum()
        cvr = (total_conv / total_clicks * 100) if total_clicks > 0 else 0
        conversion_score = min(100, int(cvr * 20)) # Benchmark 5% = 100
        
        # 4. Overall Score (Weighted Average)
        overall_score = int((intent_score * 0.4) + (waste_control_score * 0.4) + (conversion_score * 0.2))
        
        return {
            "intent_quality": intent_score,
            "waste_control": waste_control_score,
            "conversion_efficiency": conversion_score,
            "overall_score": overall_score
        }

    def cluster_keywords(self, df: pd.DataFrame, n_clusters=5) -> List[Dict]:
        """Automatically group search terms into semantic clusters for pattern detection."""
        if len(df) < n_clusters:
            return []
            
        # Select waste keywords for clustering
        waste_df = df[df['decision'] == 'NEGATIVE'].copy()
        if len(waste_df) < 2:
            return []
            
        # Vectorize
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        X = vectorizer.fit_transform(waste_df['search_term'])
        
        # K-Means
        kmeans = KMeans(n_clusters=min(n_clusters, len(waste_df)), random_state=42)
        waste_df['cluster_id'] = kmeans.fit_predict(X)
        
        # Aggregate clusters
        clusters = []
        for cid in waste_df['cluster_id'].unique():
            cluster_terms = waste_df[waste_df['cluster_id'] == cid]['search_term'].tolist()
            cluster_cost = waste_df[waste_df['cluster_id'] == cid]['cost'].sum()
            
            # Simple top term identification (just for labeling)
            label = cluster_terms[0] if cluster_terms else "Unknown Cluster"
            clusters.append({
                "label": f"Cluster: {label}",
                "terms": ", ".join(cluster_terms[:5]),
                "cost": float(cluster_cost),
                "count": len(cluster_terms)
            })
            
        # Sort by cost (most expensive waste first)
        return sorted(clusters, key=lambda x: x['cost'], reverse=True)

    def generate_phased_negatives(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Categorize negative keywords into priority phases."""
        negatives = df[df['decision'] == 'NEGATIVE']
        
        phase1 = negatives[negatives['reason'].str.contains('AI', case=False)]['search_term'].tolist()
        phase3 = negatives[negatives['reason'].str.contains('Cost', case=False)]['search_term'].tolist()
        
        # Deduplicate and fill phase 2 with generic waste
        all_neg = set(negatives['search_term'].tolist())
        phase1 = sorted(list(set(phase1)))[:20]
        phase3 = sorted(list(set(phase3)))[:20]
        phase2 = sorted(list(all_neg - set(phase1) - set(phase3)))[:20]
        
        return {
            "Phase 1 (Immediate)": phase1,
            "Phase 2 (Intent Based)": phase2,
            "Phase 3 (Data Based)": phase3
        }
